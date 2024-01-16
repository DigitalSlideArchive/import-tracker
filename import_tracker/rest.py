# -*- coding: utf-8 -*-
import time

from bson.objectid import ObjectId
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import boundHandler
from girder.constants import AccessType, SortDir
from girder.exceptions import RestException
from girder.models.assetstore import Assetstore
from girder.models.file import File
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.upload import Upload
from girder.utility import model_importer, path
from girder.utility.progress import ProgressContext, setResponseTimeLimit
from girder_jobs.constants import JobStatus
from girder_jobs.models.job import Job

from .models import AssetstoreImport, ImportTrackerCancelError


def processCursor(cursor, user):
    lookedupAssetstores = {}
    results = list(cursor)

    for row in results:
        if row['assetstoreId'] not in lookedupAssetstores:
            assetstore = list(Assetstore().find({'_id': row['assetstoreId']}))
            lookedupAssetstores[row['assetstoreId']] = assetstore[0][
                'name'] if assetstore else None

        row['_assetstoreName'] = (
            lookedupAssetstores[row['assetstoreId']] or row['assetstoreId'])
        model = model_importer.ModelImporter.model(row['params']['destinationType'])
        doc = model.load(row['params']['destinationId'], user=user)
        if doc:
            row['_destinationPath'] = path.getResourcePath(
                row['params']['destinationType'],
                doc,
                user=user
            )
        else:
            row['_destinationPath'] = 'does not exist'
    return results


def getImports(query=None, user=None, unique=False, limit=None, offset=None, sort=None):
    if not unique:
        cursor = AssetstoreImport().find(
            query or {},
            limit=limit,
            offset=offset,
            sort=sort,
        )
    else:
        cursor = AssetstoreImport().collection.aggregate([
            {'$match': query or {}},
            {'$sort': {k: v for k, v in sort}},
            {'$group': {
                '_id': {
                    'assetstoreId': '$assetstoreId',
                    'params': '$params'
                },
                '_count': {'$sum': 1},
                'started': {'$first': '$started'},
                'ended': {'$first': '$ended'}
            }},
            {'$project': {
                'assetstoreId': '$_id.assetstoreId',
                'params': '$_id.params',
                '_count': '$_count',
                'started': '$started',
                'ended': '$ended',
                '_id': None
            }},
            {'$sort': {k: v for k, v in sort}},
            {'$skip': offset or 0},
            {'$limit': limit or 0}
        ])
    return processCursor(cursor, user)


def moveFile(file, folder, user, assetstore, progress, job):
    # check if the move has been canceled
    job = Job().load(job['_id'], force=True)
    if job['status'] == JobStatus.CANCELED:
        raise ImportTrackerCancelError()

    message = f'Moving {folder["name"]}/{file["name"]}\n'
    job = Job().updateJob(job, log=f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {message}')
    progress.update(message=message)

    setResponseTimeLimit(86400)
    return Upload().moveFileToAssetstore(file, user, assetstore, progress=progress)

def moveLeafFiles(folder, user, assetstore, ignoreImported, progress, job):
    # check if the move has been canceled
    job = Job().load(job['_id'], force=True)
    if job['status'] == JobStatus.CANCELED:
        raise ImportTrackerCancelError()

    Folder().updateFolder(folder)

    # only move files that are not already in the assetstore
    query = {'assetstoreId': {'$ne': ObjectId(assetstore['_id'])}}

    # ignore imported files if desired
    if ignoreImported:
        query['imported'] = {'$ne': True}

    folder_item = Item().findOne({
        'folderId': folder['_id'],
    })
    if not folder_item:
        raise RestException('Folder %s has no item' % folder['_id'])

    child_folders = Folder().childFolders(folder, 'folder', user=user)
    child_items = Folder().childItems(folder, filters=query)

    # get all files attached to an object
    def getAttached(attachedToId):
        uploads = []
        for attached_file in File().find({'attachedToId': attachedToId, **query}):
            upload = moveFile(attached_file, folder, user, assetstore, progress, job)
            uploads.append(upload)
        return uploads

    # upload all files attached to the current folder
    uploads = getAttached(folder_item['_id'])

    for item in child_items:
        # upload all attached files for each item
        uploads += getAttached(item['_id'])

        for file in File().find({'itemId': ObjectId(item['_id']), **query}):
            upload = moveFile(file, folder, user, assetstore, progress, job)
            uploads.append(upload)

    for child_folder in child_folders:
        uploads += moveLeafFiles(child_folder, user, assetstore, ignoreImported, progress, job)

    return uploads


@access.admin
@boundHandler
@autoDescribeRoute(
    Description('List all imports for a given assetstore.')
    .param('id', 'An assetstore ID', paramType='path')
    .param('unique', 'If true, only show unique imports', required=False,
           dataType='boolean', default=False)
    .pagingParams(defaultSort='started', defaultSortDir=SortDir.DESCENDING)
)
def listImports(self, id, unique, limit, offset, sort):
    return getImports(
        {'assetstoreId': ObjectId(id)},
        self.getCurrentUser(), unique, limit, offset, sort)


@access.admin
@boundHandler
@autoDescribeRoute(
    Description('List all past imports for all assetstores.')
    .param('unique', 'If true, only show unique imports', required=False,
           dataType='boolean', default=False)
    .pagingParams(defaultSort='started', defaultSortDir=SortDir.DESCENDING)
)
def listAllImports(self, unique, limit, offset, sort):
    return getImports(
        None,
        self.getCurrentUser(), unique, limit, offset, sort)


@access.admin
@boundHandler
@autoDescribeRoute(
    Description('Move folder contents to an assetstore.')
    .modelParam('id', 'Source folder ID', model=Folder, level=AccessType.WRITE)
    .modelParam('assetstoreId', 'Destination assetstore ID', model=Assetstore, paramType='formData')
    .param('ignoreImported', 'Ignore files that have been directly imported', dataType='boolean',
           default=True, required=True)
    .param('progress', 'Whether to record progress on the move.', dataType='boolean', default=False,
           required=False)
)
def moveFolder(self, folder, assetstore, ignoreImported, progress):
    user = self.getCurrentUser()
    job = Job().createJob(
        title='Move folder "%s" to assetstore "%s"' % (folder['name'], assetstore['name']),
        type='folder_move', public=False, user=user,
    )
    job = Job().updateJob(job, '%s - Starting folder move "%s" to assetstore "%s" (%s)\n' % (
        time.strftime('%Y-%m-%d %H:%M:%S'), folder['name'], assetstore['name'], assetstore['_id']
    ), status=JobStatus.RUNNING)

    result = None
    try:
        with ProgressContext(progress, user=user,
                             title='Moving folder "%s" (%s) to assetstore "%s" (%s)' % (
                                 folder['name'],
                                 folder['_id'],
                                 assetstore['name'],
                                 assetstore['_id'])) as ctx:
            try:
                result = moveLeafFiles(folder, user, assetstore, ignoreImported, ctx, job)

                Job().updateJob(job, '%s - Finished folder move.\n' % (
                    time.strftime('%Y-%m-%d %H:%M:%S'),
                ), status=JobStatus.SUCCESS)

            except ImportTrackerCancelError:
                return 'Job canceled'

    except Exception as exc:
        Job().updateJob(job, '%s - Failed with %s\n' % (
            time.strftime('%Y-%m-%d %H:%M:%S'),
            exc,
        ), status=JobStatus.ERROR)

    return result
