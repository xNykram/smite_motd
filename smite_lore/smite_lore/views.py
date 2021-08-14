from django.shortcuts import render
from .models import Motd
from datetime import datetime, timedelta


def match_list(request):
    tomorrows = datetime.today() + timedelta(days=1)
    future = tomorrows + timedelta(days=3)
    yesterday = datetime.today() - timedelta(days=1)
    oldest_motd = yesterday - timedelta(days=30)
    todays_motd = Motd.objects.filter(date__day=datetime.today().day)
    future_motd = Motd.objects.filter(date__range=[tomorrows, future])
    archiv_motd = Motd.objects.filter(date__range=[oldest_motd, yesterday])
    test = "Test message"
    return render(request, 'motd/index.html', {'todays_motd': todays_motd, 'future_motd': future_motd,
                                               'archiv_motd': archiv_motd, 'test' : test})