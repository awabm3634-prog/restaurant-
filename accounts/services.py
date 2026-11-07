import secrets
import string

from django.core.exceptions import PermissionDenied
from django.db import transaction

from .models import BRANCH_ROLES, BranchStaff, Role, User

MANAGER_CAN_CREATE = [Role.CASHIER, Role.KITCHEN_STAFF, Role.DELIVERY_STAFF]


def creatable_roles(actor_role):
    if actor_role == Role.OWNER:
        return list(BRANCH_ROLES)
    if actor_role == Role.BRANCH_MANAGER:
        return list(MANAGER_CAN_CREATE)
    return []


def make_temp_password(length=10):
    alphabet = "".join(c for c in string.ascii_letters + string.digits if c not in "0OIl1")
    return "".join(secrets.choice(alphabet) for _ in range(length))


@transaction.atomic
def create_branch_staff(*, actor_role, branch, username, role, first_name="", email="", phone=""):
    """تنشئ User + BranchStaff معاً، وأي فشل يرجّع كل شيء."""
    if role not in creatable_roles(actor_role):
        raise PermissionDenied

    temp_password = make_temp_password()
    user = User(
        username=username,
        first_name=first_name,
        # الإيميل مطلوب وفريد في الموديل، فلو الموظف ما عنده نحط بديل
        email=email or f"{username}@staff.local",
        phone=phone or None,
        must_change_password=True,
    )
    user.set_password(temp_password)
    user.full_clean()
    user.save()

    membership = BranchStaff(user=user, branch=branch, role=role)
    membership.full_clean()
    membership.save()
    return user, temp_password
