from django.db import models


class Motd(models.Model):
    name = models.CharField(max_length=128, default="")
    description = models.CharField(max_length=1024, null=True)
    date = models.DateTimeField(blank=True, null=True)


class PrefGodsForMotd(models.Model):
    motdName = models.CharField(max_length=512)
    godID = models.IntegerField()
    godName = models.CharField(max_length=128)
    godImageUrl = models.CharField(max_length=512)
    wins = models.IntegerField(null=True)
    loses = models.IntegerField(null=True)
    ratio = models.FloatField(null=True)
    total = models.IntegerField(null=True)
