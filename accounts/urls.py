from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import StaffLoginView

app_name = "accounts"
urlpatterns = [
    path("login/", StaffLoginView.as_view(), name="staff_login"),
    path("logout/", LogoutView.as_view(), name="staff_logout"),  # POST فقط
]
