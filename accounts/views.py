from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy

from .forms import ForcedPasswordChangeForm, StaffLoginForm


class StaffLoginView(LoginView):
    template_name = "accounts/staff_login.html"
    authentication_form = StaffLoginForm
    redirect_authenticated_user = True


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
