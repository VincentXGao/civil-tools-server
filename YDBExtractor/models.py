from django.db import models


class FileInfo(models.Model):
    HashCode = models.CharField(max_length=255)
    FilePath = models.CharField(max_length=255)
    IsDeleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Hash: {self.HashCode}, Path: {self.FilePath}"
