from django.shortcuts import render
from .models import Motd
from datetime import datetime, timedelta


def match_list(request):
    tomorrow = datetime.today() + timedelta(days=1)
    tomorrow = tomorrow.replace(hour=00, minute=00)
    future = tomorrow + timedelta(days=3)
    yesterday = datetime.today() - timedelta(days=1)
    yesterday = yesterday.replace(hour=00, minute=00)
    today = datetime.today().day
    oldest_motd = yesterday - timedelta(days=30)
    todays_motd = Motd.objects.filter(date__day=today)
    future_motd = Motd.objects.filter(date__range=[tomorrow, future])
    archiv_motd = Motd.objects.filter(date__range=[oldest_motd, datetime.today()]).order_by('-date')
    return render(request, 'motd/index.html', {'todays_motd': todays_motd, 'future_motd': future_motd,
                                               'archiv_motd': archiv_motd})