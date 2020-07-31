from django.db import models
from django.contrib.postgres.fields import JSONField


class UploadFile(models.Model):
    file = models.FileField(verbose_name='arquivo')

    def __str__(self):
        return self.file.name


class ClusterData(models.Model):
    data = JSONField()


