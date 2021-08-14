from django.db import models


class Motd(models.Model):
    name = models.CharField(max_length=128, default="")
    description = models.CharField(max_length=1024, null=True)
    date = models.DateTimeField(blank=True, null=True)
