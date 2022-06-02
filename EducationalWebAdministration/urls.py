from django.contrib import admin
from django.urls import path, include

SITE_PACKAGE = "EducationalWeb"

urlpatterns = [
    path('', include(SITE_PACKAGE + ".urls")),
    path('admin/', admin.site.urls),
]
