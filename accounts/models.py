from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

MAX_MANAGERS_PER_BRANCH = 3


class Role(models.TextChoices):
    OWNER = "OWNER", "Owner"
    BRANCH_MANAGER = "BRANCH_MANAGER", "Branch Manager"
    CASHIER = "CASHIER", "Cashier"
    KITCHEN_STAFF = "KITCHEN_STAFF", "Kitchen Staff"
    DELIVERY_STAFF = "DELIVERY_STAFF", "Delivery Staff"
    CUSTOMER = "CUSTOMER", "Customer"


BRANCH_ROLES = [
    Role.BRANCH_MANAGER,
    Role.CASHIER,
    Role.KITCHEN_STAFF,
    Role.DELIVERY_STAFF,
]


class User(AbstractUser):
    email = models.EmailField("email address")
    phone = models.CharField(max_length=20, null=True, blank=True)
    is_owner = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_user_email_ci_uniq"),
            models.UniqueConstraint(
                fields=["phone"],
                condition=Q(phone__isnull=False),
                name="accounts_user_phone_uniq",
            ),
            models.CheckConstraint(
                condition=~Q(phone=""), name="accounts_user_phone_not_blank"
            ),
        ]

    def save(self, *args, **kwargs):
        self.phone = self.phone or None
        self.email = (self.email or "").strip()
        super().save(*args, **kwargs)


class BranchStaff(models.Model):
    # OneToOne: الموظف في فرع واحد فقط
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="branch_staff",
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.PROTECT,
        related_name="staff_members",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(role__in=[r.value for r in BRANCH_ROLES]),
                name="accounts_branchstaff_role_is_branch_role",
            ),
        ]
        indexes = [
            models.Index(
                fields=["branch", "role", "is_active"],
                name="accounts_bs_branch_role_idx",
            ),
        ]

    def clean(self):
        if self.user_id:
            if self.user.is_owner:
                raise ValidationError("Owner cannot be a branch staff member.")
            if hasattr(self.user, "customer_profile"):
                raise ValidationError("A customer account cannot be a branch staff member.")
        if self.branch_id and self.role == Role.BRANCH_MANAGER and self.is_active:
            managers = BranchStaff.objects.filter(
                branch_id=self.branch_id, role=Role.BRANCH_MANAGER, is_active=True
            ).exclude(pk=self.pk)
            if managers.count() >= MAX_MANAGERS_PER_BRANCH:
                raise ValidationError(
                    f"A branch can have at most {MAX_MANAGERS_PER_BRANCH} managers."
                )

    def __str__(self):
        return f"{self.user} - {self.branch} ({self.role})"


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_profile",
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(full_name="") & ~Q(phone=""),
                name="accounts_customer_name_phone_not_blank",
            ),
        ]
        indexes = [models.Index(fields=["phone"], name="accounts_customer_phone_idx")]

    def clean(self):
        if self.user_id:
            if self.user.is_owner or hasattr(self.user, "branch_staff"):
                raise ValidationError("Owner or staff accounts cannot be customers.")

    def __str__(self):
        return self.full_name
