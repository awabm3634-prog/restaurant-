from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from accounts.models import BranchStaff

from .permissions import BranchAccessMixin, OwnerRequiredMixin


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
