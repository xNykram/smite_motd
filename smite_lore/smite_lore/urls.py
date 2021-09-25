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
