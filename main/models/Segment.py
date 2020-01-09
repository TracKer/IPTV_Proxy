from django.db import models

from main.models import Source


class Segment(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='segments')
    duration = models.FloatField()
    name = models.CharField(max_length=255, null=False)
    name_original = models.CharField(max_length=255, null=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'segment'
