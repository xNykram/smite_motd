from .models import Motd, PrefGodsForMotd
from datetime import datetime, timedelta

def calcMotdList():
    tomorrow = datetime.today() + timedelta(days=1)
    tomorrow = tomorrow.replace(hour=00, minute=00)
    future = tomorrow + timedelta(days=3)
    yesterday = datetime.today() - timedelta(days=1)
    yesterday = yesterday.replace(hour=9, minute=5)
    today = datetime.today()
    oldest_motd = yesterday - timedelta(days=30)
    todays_motd = Motd.objects.filter(date__day=today.day, date__month=today.month)
    future_motd = Motd.objects.filter(date__range=[tomorrow, future])
    archiv_motd = Motd.objects.filter(date__range=[oldest_motd, yesterday]).order_by('-date')
    gods = PrefGodsForMotd.objects.all()
    return todays_motd, future_motd, archiv_motd, gods