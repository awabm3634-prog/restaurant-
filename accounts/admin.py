from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BranchStaff, Customer


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("phone", "is_owner", "must_change_password")}),
    )


@admin.register(BranchStaff)
class BranchStaffAdmin(admin.ModelAdmin):
    list_display = ("user", "branch", "role", "is_active")
    list_filter = ("branch", "role", "is_active")


admin.site.register(Customer)
