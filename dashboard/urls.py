from django.urls import path

from .views import entry, OwnerHomeView, BranchHomeView, StaffListView
from .views import StaffCreateView
from .views import StaffResetPasswordView, StaffToggleActiveView
app_name = "dashboard"
urlpatterns = [
    path("", entry, name="entry"),
    path("owner/", OwnerHomeView.as_view(), name="owner_home"),
    path("branch/<int:branch_id>/", BranchHomeView.as_view(), name="branch_home"),
    path("branch/<int:branch_id>/staff/", StaffListView.as_view(), name="staff_list"),
    path("branch/<int:branch_id>/staff/add/", StaffCreateView.as_view(), name="staff_add"),
    path("branch/<int:branch_id>/staff/<int:pk>/toggle/",
         StaffToggleActiveView.as_view(), name="staff_toggle"),
    path("branch/<int:branch_id>/staff/<int:pk>/reset-password/",
         StaffResetPasswordView.as_view(), name="staff_reset_password"),

]
