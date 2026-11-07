from django.urls import path

from .views import entry, OwnerHomeView, BranchHomeView, StaffListView

app_name = "dashboard"
urlpatterns = [
    path("", entry, name="entry"),
    path("owner/", OwnerHomeView.as_view(), name="owner_home"),
    path("branch/<int:branch_id>/", BranchHomeView.as_view(), name="branch_home"),
    path("branch/<int:branch_id>/staff/", StaffListView.as_view(), name="staff_list"),

]
