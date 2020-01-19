import os
from datetime import datetime
from os import unlink

from django.db import models
from django.utils.timezone import get_default_timezone

from IPTV_Proxy.settings import STATIC_ROOT
from main.models import Source


class Segment(models.Model):
    STATUS_NEW = 0
    STATUS_AVAILABLE = 1
    STATUS_WATCHED = 2

    _STATUSES = [
        (STATUS_NEW, 'New'),
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_WATCHED, 'Watched'),
    ]

    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='segments')
    duration = models.FloatField()
    name = models.CharField(max_length=255, null=False)
    name_original = models.CharField(max_length=255, null=False)
    url = models.CharField(max_length=255, null=False)
    status = models.PositiveSmallIntegerField(choices=_STATUSES, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'segment'

    def is_outdated(self) -> bool:
        if self.status == self.STATUS_WATCHED:
            return True

        valid_interval = self.source.get_gross_sequence_length() * self.source.SOURCE_SEQUENCES_TO_STORE

        tz = get_default_timezone()
        now = datetime.now(tz)
        interval = (now - self.updated).total_seconds()

        return interval > valid_interval

    def delete(self, using=None, keep_parents=False):
        file_path = os.path.join(STATIC_ROOT, ('segments', self.name))
        unlink(file_path)
        return super().delete(using, keep_parents)
