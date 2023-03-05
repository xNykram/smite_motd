from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

app_name = "app"

sitemaps = {
    'static': StaticViewSitemap,
}


urlpatterns = [
    path('', views.match_list, name="motd"),
    path('stats', views.stats, name="stats"),
    path('tierlist', views.tierlist, name="tierlist"),
    path('contact', views.contact, name="contact"),
    path('adminpanel', admin.site.urls, name="admin"),
    path('sitemap', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
]

handler500 = 'app.views.handler500'
handler404 = 'app.views.handler404'
handler403 = 'app.views.handler403'
handler400 = 'app.views.handler400'
