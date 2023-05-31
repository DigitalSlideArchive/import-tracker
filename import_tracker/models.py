import threading
from datetime import datetime

from bson.objectid import ObjectId
from girder.events import Event
from girder.exceptions import ValidationException
from girder.models.model_base import Model


class AssetstoreImport(Model):
    """A model that tracks assetstore import events."""

    def initialize(self):
        self.name = 'assetstoreImport'
        self._recentParamsLock = threading.RLock()
        self._recentParams = []
        self._recentParamsMaxSize = 100

    def validate(self, doc):
        fields = {'name', 'started', 'assetstoreId', 'params'}
        missing_keys = fields - doc.keys()
        if missing_keys:
            raise ValidationException('Fields missing.', ','.join(missing_keys))

        return doc

    def createAssetstoreImport(self, event: Event):
        now = datetime.utcnow()
        record = self.save(
            {
                'name': now.isoformat(),
                'started': now,
                'assetstoreId': ObjectId(event.info['id']),
                'params': {k: v for k, v in sorted(event.info['params'].items())},
            }
        )
        with self._recentParamsLock:
            self._recentParams = self._recentParams[-self._recentParamsMaxSize:]
            self._recentParams.append((record, event.info['params']))
        return record

    def updateAssetstoreImport(self, event: Event):
        record = None
        with self._recentParamsLock:
            for idx, (rrecord, rparams) in enumerate(self._recentParams):
                if event.info['params'] is rparams:
                    record = rrecord
                    self._recentParams.pop(idx)
                    break
        if record:
            now = datetime.utcnow()
            record = self.load(id=record['_id'])
            record['ended'] = now
            record = self.save(record)
