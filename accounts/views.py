from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy

from .forms import ForcedPasswordChangeForm, StaffLoginForm


from django.shortcuts import redirect

from .services import has_dashboard_access


class StaffLoginView(LoginView):
    template_name = "accounts/staff_login.html"
    authentication_form = StaffLoginForm
    redirect_authenticated_user = False  # نتحكم بالتحويل يدوياً

    def dispatch(self, request, *args, **kwargs):
        if has_dashboard_access(request.user):
            return redirect("dashboard:entry")
        return super().dispatch(request, *args, **kwargs)

class ForcedPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = ForcedPasswordChangeForm
    success_url = reverse_lazy("dashboard:entry")

    def form_valid(self, form):
        response = super().form_valid(form)  # يحفظ الباسورد ويبقي الجلسة
        user = self.request.user
        user.must_change_password = False
        user.save(update_fields=["must_change_password"])
        return response
