from django import forms
from django.db.models import Q

from .models import Category, MenuItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "sort_order", "is_active"]
        labels = {"name": "الاسم", "sort_order": "الترتيب", "is_active": "فعّال"}

    def __init__(self, *args, branch, **kwargs):
        super().__init__(*args, **kwargs)
        self.branch = branch
        self.instance.branch = branch  # الفرع من الرابط، مو من الفورم

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        exists = (
            Category.objects.filter(branch=self.branch, name__iexact=name)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if exists:
            raise forms.ValidationError("يوجد تصنيف بهذا الاسم في الفرع.")
        return name


class ItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["category", "name", "description", "price", "is_available", "is_active"]
        labels = {
            "category": "التصنيف", "name": "الاسم", "description": "الوصف",
            "price": "السعر", "is_available": "متوفر الآن", "is_active": "ظاهر في المنيو",
        }

    def __init__(self, *args, branch, **kwargs):
        super().__init__(*args, **kwargs)
        # تصنيفات هذا الفرع فقط، فما يقدر أحد يربط طبقاً بتصنيف فرع آخر
        self.fields["category"].queryset = Category.objects.filter(
            Q(branch=branch) & (Q(is_active=True) | Q(pk=self.instance.category_id))
        )
