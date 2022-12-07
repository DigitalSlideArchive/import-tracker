# -*- coding: utf-8 -*-
from bson.objectid import ObjectId
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import boundHandler
from girder.constants import SortDir
from girder.models.assetstore import Assetstore
from girder.utility import model_importer, path

from .models import AssetstoreImport


def processCursor(cursor, user):
    lookedupAssetstores = {}
    results = list(cursor)

    for row in results:
        if row['assetstoreId'] not in lookedupAssetstores:
            assetstore = list(Assetstore().find({'_id': row['assetstoreId']}))
            lookedupAssetstores[row['assetstoreId']] = assetstore[0]['name']

        row['_assetstoreName'] = lookedupAssetstores[row['assetstoreId']]
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


@access.admin
@boundHandler
@autoDescribeRoute(
    Description('List all imports for a given assetstore.')
    .param('id', '', 'path')
    .pagingParams(defaultSort='started', defaultSortDir=SortDir.DESCENDING)
)
def listImports(self, id, limit, offset, sort):
    cursor = AssetstoreImport().find(
        {'assetstoreId': ObjectId(id)},
        limit=limit,
        offset=offset,
        sort=sort,
    )
    user = self.getCurrentUser()
    imports = processCursor(cursor, user)

    return imports


@access.admin
@boundHandler
@autoDescribeRoute(
    Description('List all past imports for all assetstores.')
    .pagingParams(defaultSort='started', defaultSortDir=SortDir.DESCENDING)
)
def listAllImports(self, limit, offset, sort):
    cursor = AssetstoreImport().find(
        limit=limit,
        offset=offset,
        sort=sort,
    )
    user = self.getCurrentUser()
    imports = processCursor(cursor, user)

    return imports
