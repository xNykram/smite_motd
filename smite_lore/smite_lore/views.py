from django.shortcuts import render
from .common import calcMotdList


def match_list(request):
    data = calcMotdList()
    return render(request, 'motd.html', {'todays_motd': data[0], 'future_motd': data[1],
                                               'archiv_motd': data[2], 'gods': data[3]})

def stats(request):
    return render(request, 'stats.html')


def analyzer(request):
    return render(request, 'analyzer.html')


def contact(request):
    return render(request, 'contact.html')

