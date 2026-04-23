from django.contrib import messages
from django.shortcuts import redirect
from django.views.csrf import csrf_failure as default_csrf_failure


def csrf_failure(request, reason="", template_name="403_csrf.html"):
    """Handle stale CSRF tokens on admin login by issuing a fresh login form."""
    if request.method == "POST" and request.path.startswith("/admin/login"):
        messages.error(
            request,
            "Tu token de seguridad expiro. Intenta iniciar sesion nuevamente.",
        )
        return redirect(request.path)

    return default_csrf_failure(request, reason=reason, template_name=template_name)
