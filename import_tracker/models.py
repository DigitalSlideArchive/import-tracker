from bson.objectid import ObjectId
from datetime import datetime
from girder.events import Event
from girder.models.model_base import Model
from girder.exceptions import ValidationException


class AssetstoreImport(Model):
    """A model that tracks assetstore import events."""

    def initialize(self):
        self.name = "assetstoreImport"

    def validate(self, doc):
        # fields = {"name", "started", "completed", "assetstoreId", "params"}
        fields = {"name", "started", "assetstoreId", "params"}
        missing_keys = doc.keys() - fields
        if missing_keys:
            raise ValidationException("Fields missing.", ",".join(missing_keys))

        return doc

    def createAssetstoreImport(self, event: Event):
        now = datetime.utcnow()
        return self.save(
            {
                "name": now.isoformat(),
                "started": now,
                # "completed": None,
                "assetstoreId": ObjectId(event.info["id"]),
                "params": event.info["params"],
            }
        )

    def finishAssetstoreImport(self, event: Event):
        pass
