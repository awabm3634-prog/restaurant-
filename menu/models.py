from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class Category(models.Model):
    branch = models.ForeignKey(
        "branches.Branch", on_delete=models.PROTECT, related_name="menu_categories"
    )
    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "categories"
        constraints = [
            # الاسم فريد داخل الفرع الواحد، بدون حساسية للحروف
            models.UniqueConstraint(
                Lower("name"), "branch", name="menu_category_branch_name_ci_uniq"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.branch})"


class MenuItem(models.Model):
    # الفرع يجي من التصنيف (مصدر واحد للحقيقة)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="items"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    is_available = models.BooleanField(default=True)  # إيقاف سريع (خلص المكوّن)
    is_active = models.BooleanField(default=True)  # إخفاء بدل الحذف
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "category", name="menu_item_category_name_ci_uniq"
            ),
            models.CheckConstraint(
                condition=Q(price__gte=0), name="menu_item_price_non_negative"
            ),
        ]
        indexes = [
            models.Index(fields=["category", "is_active"], name="menu_item_cat_active_idx"),
        ]

    @property
    def branch(self):
        return self.category.branch

    def clean(self):
        if self.name is not None and not self.name.strip():
            raise ValidationError("اسم الطبق مطلوب.")

    def __str__(self):
        return self.name
