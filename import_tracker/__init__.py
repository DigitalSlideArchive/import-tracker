import girder.api.v1.assetstore
from girder import events, plugin
from girder.utility.model_importer import ModelImporter

from import_tracker.models import AssetstoreImport
from import_tracker.rest import listAllImports, listImports

girder.api.v1.assetstore.Assetstore.importData.description.param(
    'flag',
    'Whether folders containing only files should be imported as items.',
    dataType='boolean', required=False, default=False)


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'import_tracker'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        ModelImporter.registerModel(
            'assetstoreImport', AssetstoreImport, 'import_tracker'
        )
        events.bind(
            'rest.post.assetstore/:id/import.before',
            'create_assetstore_import',
            AssetstoreImport().createAssetstoreImport,
        )
        events.bind(
            'rest.post.assetstore/:id/import.after',
            'update_assetstore_import',
            AssetstoreImport().updateAssetstoreImport,
        )

        # API
        info['apiRoot'].assetstore.route('GET', (':id', 'imports'), listImports)
        info['apiRoot'].assetstore.route('GET', ('all_imports',), listAllImports)
