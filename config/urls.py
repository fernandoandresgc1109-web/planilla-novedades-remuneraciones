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
    path(
        "cuentas/password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url="/cuentas/password_change/done/",
        ),
        name="password_change",
    ),
    path(
        "cuentas/password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html",
        ),
        name="password_change_done",
    ),
    path("", include("novedades.urls")),
]