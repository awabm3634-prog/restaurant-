from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from accounts.models import BranchStaff, Role
from branches.models import Branch


class OwnerRequiredMixin(AccessMixin):
    """المالك فقط."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()  # يحوّل للـ login
        if not request.user.is_owner:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class BranchAccessMixin(AccessMixin):
    """المالك يدخل أي فرع، والموظف يدخل فرعه فقط."""

    allowed_roles = None  # None = أي دور داخل الفرع

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        branch_id = kwargs["branch_id"]
        if request.user.is_owner:
            self.branch = get_object_or_404(Branch, pk=branch_id)
            self.role = Role.OWNER
        else:
            membership = (
                BranchStaff.objects.select_related("branch")
                .filter(
                    user=request.user,
                    branch_id=branch_id,
                    is_active=True,
                    branch__is_active=True,
                )
                .first()
            )
            if membership is None:
                raise PermissionDenied  # 403 حتى لو الفرع غير موجود، فما نكشف وجوده
            self.branch = membership.branch
            self.role = membership.role

        if self.allowed_roles and self.role not in self.allowed_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["branch"] = self.branch
        context["role"] = self.role
        return context
