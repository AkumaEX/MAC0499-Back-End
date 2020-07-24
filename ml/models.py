# Create your models here.
from django.db import models


class UploadFile(models.Model):
    file = models.FileField(verbose_name='arquivo')

    def __str__(self):
        return self.file.name
