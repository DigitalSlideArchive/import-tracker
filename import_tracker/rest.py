# -*- coding: utf-8 -*-
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.constants import SortDir
from .models import AssetstoreImport

from bson.objectid import ObjectId


@access.admin
@autoDescribeRoute(
    Description('List all imports for a given assetstore.')
    .param('id', '', 'path')
    .pagingParams(defaultSort='started', defaultSortDir=SortDir.DESCENDING)
)
def listImports(id, limit, offset, sort):
    return AssetstoreImport().find(
        {'assetstoreId': ObjectId(id)},
        limit=limit,
        offset=offset,
        sort=sort,
    )


@access.admin
@autoDescribeRoute(
    Description('List all past imports for all assetstores.')
    .pagingParams(defaultSort='started', defaultSortDir=SortDir.DESCENDING)
)
def listAllImports(limit, offset, sort):
    return AssetstoreImport().find(
        limit=limit,
        offset=offset,
        sort=sort,
    )
