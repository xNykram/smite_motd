from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['motd', 'stats', 'analyzer', 'contact']

    def location(self, item):
        return reverse(item)
