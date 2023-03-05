from django.contrib import admin
from .models import Tierlist, PrefGodsForMotd, Motd, Logs

admin.site.register(Motd)
admin.site.register(PrefGodsForMotd)
admin.site.register(Tierlist)
admin.site.register(Logs)