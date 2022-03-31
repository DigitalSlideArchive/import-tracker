from girder import plugin, events
from girder.utility.model_importer import ModelImporter

from import_tracker.models import AssetstoreImport


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = "import_tracker"
    CLIENT_SOURCE_PATH = "web_client"

    def load(self, info):
        ModelImporter.registerModel("image", AssetstoreImport, "import_tracker")
        events.bind(
            "rest.post.assetstore/:id/import.before",
            "create_assetstore_import",
            AssetstoreImport().createAssetstoreImport,
        )
