from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import StaffLoginView, ForcedPasswordChangeView

app_name = "accounts"
urlpatterns = [
    path("login/", StaffLoginView.as_view(), name="staff_login"),
    path("logout/", LogoutView.as_view(), name="staff_logout"),  # POST فقط
    path("password-change/", ForcedPasswordChangeView.as_view(), name="password_change"),

]
