from django import forms

from accounts.models import Role


class StaffCreateForm(forms.Form):
    username = forms.CharField(label="اسم المستخدم", max_length=150)
    first_name = forms.CharField(label="الاسم", max_length=150, required=False)
    role = forms.ChoiceField(label="الدور")
    phone = forms.CharField(label="الهاتف", max_length=20, required=False)
    email = forms.EmailField(label="الإيميل (اختياري)", required=False)

    def __init__(self, *args, allowed_roles, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = [(r.value, r.label) for r in allowed_roles]
