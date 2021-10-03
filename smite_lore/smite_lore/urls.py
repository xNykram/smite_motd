from django.urls import path
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
    path('tierlist', views.tierlist, name="tierlist"),
    path('contact', views.contact, name="contact"),
    path('sitemap', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
]

handler500 = 'smite_lore.views.handler500'
handler404 = 'smite_lore.views.handler404'
handler403 = 'smite_lore.views.handler403'
handler400 = 'smite_lore.views.handler400'
