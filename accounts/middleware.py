from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """أي مستخدم must_change_password=True ما يشوف أي صفحة غير تغيير كلمة المرور."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and user.must_change_password:
            allowed = (
                reverse("accounts:password_change"),
                reverse("accounts:staff_logout"),
            )
            if request.path not in allowed:
                return redirect("accounts:password_change")
        return self.get_response(request)
