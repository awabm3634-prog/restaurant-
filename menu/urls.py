from django.urls import path

from . import views

app_name = "menu"
urlpatterns = [
    path("", views.MenuListView.as_view(), name="list"),
    path("categories/add/", views.CategoryCreateView.as_view(), name="category_add"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_edit"),
    path("items/add/", views.ItemCreateView.as_view(), name="item_add"),
    path("items/<int:pk>/edit/", views.ItemUpdateView.as_view(), name="item_edit"),
    path("items/<int:pk>/toggle/", views.ItemToggleAvailableView.as_view(), name="item_toggle"),
]
