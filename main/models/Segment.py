from django.db import models

from main.models import Source


class Segment(models.Model):
    _STATUSES = [
        (0, 'New'),
        (1, 'Available'),
        (2, 'Watched')
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
