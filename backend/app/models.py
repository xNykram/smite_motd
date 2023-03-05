from django.db import models


class Motd(models.Model):
    name = models.CharField(max_length=128, default="")
    description = models.CharField(max_length=1024, null=True)
    date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "Motd: {} {}".format(self.name, self.date)


class PrefGodsForMotd(models.Model):
    motdName = models.CharField(max_length=512)
    godID = models.IntegerField()
    godName = models.CharField(max_length=128)
    godImageUrl = models.CharField(max_length=512)
    wins = models.IntegerField(null=True)
    loses = models.IntegerField(null=True)
    ratio = models.FloatField(null=True)
    total = models.IntegerField(null=True)

    def __str__(self):
        return "Motd {} best god {}".format(self.motdName, self.godName)


class Tierlist(models.Model):
    godName = models.CharField(max_length=128)
    mode = models.CharField(max_length=64)
    rank = models.CharField(max_length=12)
    winrate = models.FloatField(null=True)
    date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "Rank {} {}".format(self.rank, self.godName)


class Logs(models.Model):

    type = models.CharField(max_length=32)
    loginfo = models.CharField(max_length=16)
    response = models.CharField(max_length=512)
    host = models.CharField(max_length=64)
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table ='logs'
        verbose_name_plural = "Logs"

    def __str__(self):
        return "Action: {} Response: {} ResponseInfo: {}, TriggeredBy: {}, Date {}".format(
            self.type, self.loginfo, self.response, self.host, self.date
        )