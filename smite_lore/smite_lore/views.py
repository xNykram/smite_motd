from django.shortcuts import render
from .common import calcMotdList
from .models import Tierlist

def match_list(request):
    data = calcMotdList()
    return render(request, 'motd.html', {'todays_motd': data[0], 'future_motd': data[1],
                                               'archiv_motd': data[2], 'gods': data[3]})

def stats(request):
    return render(request, 'stats.html')


def tierlist(request):
    tierlist = Tierlist.objects.all().filter(mode='Conquest(R)')
    print(tierlist)
    return render(request, 'tierlist.html', {'tierlistgods': tierlist})



def contact(request):
    return render(request, 'contact.html')


def handler404(request, exception):
    return render(request, "404.html", {})


def handler500(request):
    return render(request, "500.html", {})


def handler403(request, exception):
    return render(request, "403.html", {})


def handler400(request, exception):
    return render(request, "400.html", {})
