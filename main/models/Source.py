from datetime import datetime

from django.db import models
from django.utils.timezone import get_default_timezone


class Source(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False)
    url = models.CharField(max_length=255, null=False)
    last_sequence = models.PositiveIntegerField()
    target_duration = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    requested = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'source'

    def get_request_interval(self) -> int:
        return round(self.target_duration / 2)

    def is_outdated(self) -> bool:
        # Outdated if last accessed >= (target_duration * 4)
        tz = get_default_timezone()
        now = datetime.now(tz)
        interval = (now - self.requested).total_seconds()
        return interval >= (self.target_duration * 4)
