from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import ListView, TemplateView

from accounts.models import BranchStaff, Role

from .permissions import BranchAccessMixin, OwnerRequiredMixin

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
