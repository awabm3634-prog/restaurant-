from django.contrib import admin

from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "branch", "sort_order", "is_active")
    list_filter = ("branch", "is_active")
    search_fields = ("name",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available", "is_active")
    list_filter = ("category__branch", "category", "is_available", "is_active")
    search_fields = ("name",)
