"""smite_lore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf.urls import url
from . import views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

app_name = "smite_lore"

sitemaps = {
    'static': StaticViewSitemap,
}


urlpatterns = [
    path('', views.match_list, name="motd"),
    path('stats', views.stats, name="stats"),
    path('analyzer', views.analyzer, name="analyzer"),
    path('contact', views.contact, name="contact"),
    path('sitemap', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
]
