from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import BranchStaff

GENERIC_ERROR = "بيانات الدخول غير صحيحة."


class StaffLoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": GENERIC_ERROR,
        "inactive": GENERIC_ERROR,
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)  # الحساب فعّال

        if user.is_owner:
            return  # المالك يكفيه حساب فعّال

        if hasattr(user, "customer_profile"):
            raise ValidationError(GENERIC_ERROR, code="invalid_login")

        has_active_membership = BranchStaff.objects.filter(
            user=user, is_active=True, branch__is_active=True
        ).exists()
        if not has_active_membership:
            raise ValidationError(GENERIC_ERROR, code="invalid_login")
