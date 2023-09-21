# -*- coding: utf-8 -*-
from bson.objectid import ObjectId
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import boundHandler
from girder.constants import AccessType, SortDir
from girder.models.assetstore import Assetstore
from girder.models.file import File
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.upload import Upload
from girder.utility import model_importer, path

from .models import AssetstoreImport


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


def moveLeafFiles(folder, user, assetstore):
    Folder().updateFolder(folder)

    folder_item = Item().findOne({
        'folderId': folder['_id'],
    })
    unique_clause = {'assetstoreId': {'$ne': ObjectId(assetstore['_id'])}}

    child_folders = Folder().childFolders(folder, 'folder', user=user)
    child_items = Folder().childItems(folder, filters=unique_clause)

    results = []
    for attached_file in File().find({
        'attachedToId': folder_item['_id'],
        **unique_clause
    }):
        results.append(Upload().moveFileToAssetstore(attached_file, user, assetstore))

    for item in child_items:
        for file in File().find({'itemId': ObjectId(item['_id']), **unique_clause}):
            results.append(Upload().moveFileToAssetstore(file, user, assetstore))

    for child_folder in child_folders:
        results += moveLeafFiles(child_folder, user, assetstore)

    return results


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
)
def moveFolder(self, folder, assetstore):
    return moveLeafFiles(folder, self.getCurrentUser(), assetstore)
