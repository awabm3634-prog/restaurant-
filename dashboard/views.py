from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import ListView, TemplateView

from accounts.models import BranchStaff, Role

from .permissions import BranchAccessMixin, OwnerRequiredMixin

from django.core.exceptions import ValidationError
from django.views.generic import FormView

from accounts.services import create_branch_staff, creatable_roles

from .forms import StaffCreateForm

MANAGEMENT_ROLES = [Role.BRANCH_MANAGER, Role.OWNER]


@login_required
def entry(request):
    user = request.user
    if user.is_owner:
        return redirect("dashboard:owner_home")
    staff = BranchStaff.objects.filter(
        user=user, is_active=True, branch__is_active=True
    ).first()
    if not staff:
        return render(request, "dashboard/no_access.html", status=403)
    return redirect("dashboard:branch_home", branch_id=staff.branch_id)


class OwnerHomeView(OwnerRequiredMixin, TemplateView):
    template_name = "dashboard/owner_home.html"


class BranchHomeView(BranchAccessMixin, TemplateView):
    template_name = "dashboard/branch_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "home"
        context["staff_count"] = BranchStaff.objects.filter(
            branch=self.branch, is_active=True
        ).count()
        return context


class StaffListView(BranchAccessMixin, ListView):
    allowed_roles = MANAGEMENT_ROLES
    template_name = "dashboard/staff_list.html"
    context_object_name = "staff"

    def get_queryset(self):
        # الفلترة بـ self.branch هي اللي تعزل الفروع فعلياً
        return (
            BranchStaff.objects.filter(branch=self.branch)
            .select_related("user")
            .order_by("role", "user__username")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "staff"
        return context

#------------------------------•------------------------


class StaffCreateView(BranchAccessMixin, FormView):
    allowed_roles = MANAGEMENT_ROLES
    template_name = "dashboard/staff_form.html"
    form_class = StaffCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["allowed_roles"] = creatable_roles(self.role)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "staff"
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            user, temp_password = create_branch_staff(
                actor_role=self.role,
                branch=self.branch,
                username=data["username"],
                role=data["role"],
                first_name=data["first_name"],
                email=data["email"],
                phone=data["phone"],
            )
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        # نعرض البيانات مرة واحدة ولا نخزنها في أي مكان
        context = self.get_context_data(new_user=user, temp_password=temp_password)
        return render(self.request, "dashboard/staff_created.html", context)
