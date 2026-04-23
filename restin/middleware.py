import re

from django.shortcuts import redirect


class KitchenOnlyMiddleware:
    """
    Restrict kitchen, waiter and cashier users to role-specific routes only.
    """

    KITCHEN_ROLE_ID = 3

    ALLOWED_PREFIXES = (
        "/ventas/pedidos/cocina/",
        "/ventas/api/pedidos/activos/",
        "/cocina/",
        "/accounts/logout/",
        "/logout/",
        "/admin/logout/",
        "/static/",
    )

    ALLOWED_PATTERNS = (
        re.compile(r"^/ventas/pedidos/\d+/(listo|entregada)/$"),
    )

    WAITER_ALLOWED_PATHS = {
        "/ventas/",
        "/ventas",
        "/ventas/pedidos/",
        "/ventas/pedidos",
        "/ventas/pedidos/nuevo/",
        "/ventas/pedidos/nuevo",
    }

    WAITER_ALLOWED_PATTERNS = (
        re.compile(r"^/ventas/pedidos/\d+/$"),
        re.compile(r"^/ventas/pedidos/\d+/confirmar/$"),
        re.compile(r"^/ventas/pedidos/\d+/items/\d+/(incrementar|disminuir|eliminar)/$"),
    )

    CASHIER_ALLOWED_PATHS = {
        "/ventas/",
        "/ventas",
        "/ventas/pedidos/",
        "/ventas/pedidos",
        "/ventas/ventas/historial/",
        "/ventas/ventas/historial",
    }

    CASHIER_ALLOWED_PATTERNS = (
        re.compile(r"^/ventas/pedidos/\d+/pagado/$"),
        re.compile(r"^/ventas/ventas/historial/exportar/$"),
    )

    COMMON_ALLOWED_PREFIXES = (
        "/accounts/logout/",
        "/logout/",
        "/admin/logout/",
        "/static/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            profile = getattr(user, "userprofile", None)
            role = getattr(profile, "role", None)
            role_name = (role.name or "").strip().lower() if role else ""
            role_id = getattr(profile, "role_id", None)
            path = request.path

            if role_name == "kitchen" or role_id == self.KITCHEN_ROLE_ID:
                is_allowed = path.startswith(self.ALLOWED_PREFIXES) or any(
                    pattern.match(path) for pattern in self.ALLOWED_PATTERNS
                )

                if not is_allowed:
                    return redirect("/cocina/")

            if role_name == "waiter":
                is_allowed = (
                    path in self.WAITER_ALLOWED_PATHS
                    or path.startswith(self.COMMON_ALLOWED_PREFIXES)
                    or any(pattern.match(path) for pattern in self.WAITER_ALLOWED_PATTERNS)
                )
                if not is_allowed:
                    return redirect("/ventas/")

            if role_name == "cashier":
                is_allowed = (
                    path in self.CASHIER_ALLOWED_PATHS
                    or path.startswith(self.COMMON_ALLOWED_PREFIXES)
                    or any(pattern.match(path) for pattern in self.CASHIER_ALLOWED_PATTERNS)
                )
                if not is_allowed:
                    return redirect("/ventas/")

        return self.get_response(request)
