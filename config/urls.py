from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("novedades.api_urls")),
    path("cuentas/", include("django.contrib.auth.urls")),
    path("", include("novedades.urls")),
]