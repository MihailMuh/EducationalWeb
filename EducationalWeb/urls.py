from django.conf import settings
from django.urls import path
from django.views.decorators.cache import cache_page

from .views import sign, diary, get_html_page, enter


def cache_if_not_debug(view):
    if not settings.DEBUG:
        return cache_page(60 * 15)(view)
    return view


urlpatterns = [
    path('', cache_if_not_debug(sign)),
    path('diary', cache_if_not_debug(diary)),
    path('html', cache_if_not_debug(get_html_page)),

    path('enter', enter)
]
