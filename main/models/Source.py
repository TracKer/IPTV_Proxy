from datetime import datetime

from django.db import models
from django.utils.timezone import get_default_timezone


class Source(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False)
    url = models.CharField(max_length=255, null=False)
    last_sequence = models.PositiveIntegerField()
    target_duration = models.PositiveIntegerField()
    segments_per_file = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    requested = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'source'

    def get_request_interval(self) -> int:
        # Request interval is a half of target_duration - average segment length
        return round(self.target_duration / 2)

    def is_outdated(self) -> bool:
        # Outdated if no requests for (target_duration * segments_per_file) seconds - time of all segments in file
        tz = get_default_timezone()
        now = datetime.now(tz)
        interval = (now - self.requested).total_seconds()
        return interval >= (self.target_duration * self.segments_per_file)
