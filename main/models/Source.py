import hashlib
from datetime import datetime

from django.db import models
from django.utils.timezone import get_default_timezone


class Source(models.Model):
    SOURCE_SEQUENCES_TO_STORE = 3

    name = models.CharField(max_length=64, unique=True, null=False)
    url = models.CharField(max_length=255, null=False)
    last_sequence = models.PositiveIntegerField()
    target_duration = models.PositiveIntegerField()
    segments_per_file = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    requested_by_client = models.DateTimeField(auto_now_add=True)
    requested_by_server = models.DateTimeField(null=True)

    class Meta:
        db_table = 'source'

    def get_request_interval(self) -> int:
        # Request interval is a half of target_duration - average segment length
        return round(self.target_duration / 2)

    def is_source_outdated(self) -> bool:
        tz = get_default_timezone()
        now = datetime.now(tz)
        interval = (now - self.requested_by_client).total_seconds()
        return interval > (self.get_gross_sequence_length() * self.SOURCE_SEQUENCES_TO_STORE)

    def is_data_outdated(self) -> bool:
        if self.requested_by_server is None:
            return True
        tz = get_default_timezone()
        now = datetime.now(tz)
        interval = (now - self.requested_by_server).total_seconds()
        return interval > self.get_request_interval()

    def get_estimated_sequence_length(self) -> int:
        """
        May be a little less then real sequence length
        """
        return self.get_gross_sequence_length() - self.segments_per_file

    def get_gross_sequence_length(self) -> int:
        """
        May be a little more then real sequence length
        """
        return self.target_duration * self.segments_per_file

    @staticmethod
    def generate_name(url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()
