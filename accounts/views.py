from django.contrib.auth.views import LoginView

from .forms import StaffLoginForm


class StaffLoginView(LoginView):
    template_name = "accounts/staff_login.html"
    authentication_form = StaffLoginForm
    redirect_authenticated_user = True
