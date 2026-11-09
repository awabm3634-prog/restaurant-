from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, TemplateView, UpdateView, View

from accounts.models import Role
from dashboard.permissions import BranchAccessMixin

from .forms import CategoryForm, ItemForm
from .models import Category, MenuItem

MANAGEMENT_ROLES = [Role.BRANCH_MANAGER, Role.OWNER]


class MenuMixin(BranchAccessMixin):
    allowed_roles = MANAGEMENT_ROLES

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "menu"
        return context


class FormPageMixin(MenuMixin):
    template_name = "menu/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["branch"] = self.branch
        return kwargs

    def get_success_url(self):
        return reverse("menu:list", kwargs={"branch_id": self.branch.id})

    def form_valid(self, form):
        messages.success(self.request, "تم الحفظ.")
        return super().form_valid(form)


class MenuListView(MenuMixin, TemplateView):
    template_name = "menu/menu_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(
            branch=self.branch
        ).prefetch_related("items")
        return context


class ItemFormMixin(FormPageMixin):
    model = MenuItem
    form_class = ItemForm
    title = "الطبق"

    def get_queryset(self):
        # فلتر الفرع: طبق من فرع آخر = 404
        return MenuItem.objects.filter(category__branch=self.branch)


class ItemCreateView(ItemFormMixin, CreateView):
    pass


class ItemUpdateView(ItemFormMixin, UpdateView):
    pass


class CategoryFormMixin(FormPageMixin):
    model = Category
    form_class = CategoryForm
    title = "التصنيف"

    def get_queryset(self):
        return Category.objects.filter(branch=self.branch)


class CategoryCreateView(CategoryFormMixin, CreateView):
    pass


class CategoryUpdateView(CategoryFormMixin, UpdateView):
    pass


class ItemToggleAvailableView(MenuMixin, View):
    http_method_names = ["post"]

    def post(self, request, branch_id, pk):
        item = get_object_or_404(MenuItem, pk=pk, category__branch=self.branch)
        item.is_available = not item.is_available
        item.save(update_fields=["is_available"])
        return redirect("menu:list", branch_id=self.branch.id)
