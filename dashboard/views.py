from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import ListView, TemplateView

from accounts.models import BranchStaff, Role

from .permissions import BranchAccessMixin, OwnerRequiredMixin

from django.core.exceptions import ValidationError
from django.views.generic import FormView

from accounts.services import create_branch_staff, creatable_roles

from .forms import StaffCreateForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.generic import View

from accounts.services import reset_staff_password, set_staff_active

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
        return (
            BranchStaff.objects.filter(branch=self.branch)
            .select_related("user")
            .order_by("role", "user__username")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "staff"
        context["manageable"] = creatable_roles(self.role)
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
#———————------------------------------------------------------------
class StaffActionMixin(BranchAccessMixin):
    allowed_roles = MANAGEMENT_ROLES
    http_method_names = ["post"]  # الإجراءات POST فقط

    def get_membership(self, pk):
        # فلتر branch=self.branch يمنع لمس موظف فرع آخر حتى بتخمين الرقم
        return get_object_or_404(
            BranchStaff.objects.select_related("user"), pk=pk, branch=self.branch
        )


class StaffToggleActiveView(StaffActionMixin, View):
    def post(self, request, branch_id, pk):
        membership = self.get_membership(pk)
        new_state = not membership.is_active
        try:
            set_staff_active(
                actor_role=self.role,
                actor=request.user,
                membership=membership,
                active=new_state,
            )
        except ValidationError as e:
            messages.error(request, " ".join(e.messages))
        else:
            word = "تفعيل" if new_state else "تعطيل"
            messages.success(request, f"تم {word} {membership.user.username}.")
        return redirect("dashboard:staff_list", branch_id=self.branch.id)


class StaffResetPasswordView(StaffActionMixin, View):
    def post(self, request, branch_id, pk):
        membership = self.get_membership(pk)
        temp_password = reset_staff_password(
            actor_role=self.role, actor=request.user, membership=membership
        )
        return render(
            request,
            "dashboard/staff_password_reset.html",
            {
                "branch": self.branch,
                "role": self.role,
                "active": "staff",
                "member": membership,
                "temp_password": temp_password,
            },
        )
