from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("novedades.api_urls")),
        path(
        "cuentas/login/",
        auth_views.LoginView.as_view(),
        name="login",
    ),
    path(
        "cuentas/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("", include("novedades.urls")),
]