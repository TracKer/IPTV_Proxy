from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False)
    url = models.CharField(max_length=255, null=False)
    created = models.DateTimeField(auto_now_add=True)
    requested = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'source'
