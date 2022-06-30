from django.urls import path

from .views import sign, diary, get_html_page, enter

urlpatterns = [
    path('', sign),
    path('diary', diary),
    path('html', get_html_page),

    path('enter', enter)
]
