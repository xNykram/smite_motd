from django.http import HttpResponse
from django.shortcuts import render

def match_list(request):
    return render(request, 'motd/index.html')