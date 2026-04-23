from django.contrib.auth.views import LoginView
from django.core.cache import cache


MAX_ATTEMPTS = 5
BLOCK_TIME = 15 * 60
SESSION_FLAG = 'login_rate_limited'


def get_cache_key(username, ip_address):
    return f'login_attempts:{username}:{ip_address}'


class RateLimitedLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        profile = getattr(self.request.user, 'userprofile', None)
        role = getattr(profile, 'role', None)
        role_name = (role.name or '').strip().lower() if role else ''
        if role_name == 'kitchen' or getattr(profile, 'role_id', None) == 3:
            return '/cocina/'
        if role_name == 'waiter':
            return '/ventas/'
        if role_name == 'cashier':
            return '/ventas/'
        return super().get_success_url()

    def get_client_ip(self):
        forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR', '')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rate_limited'] = self.request.session.get(SESSION_FLAG, False)
        return context

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '')
        cache_key = get_cache_key(username, self.get_client_ip())
        attempts = cache.get(cache_key, 0)

        if attempts >= MAX_ATTEMPTS:
            request.session[SESSION_FLAG] = True
            return self.get(request, *args, **kwargs)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        cache_key = get_cache_key(form.get_user().get_username(), self.get_client_ip())
        cache.delete(cache_key)
        self.request.session[SESSION_FLAG] = False
        return super().form_valid(form)

    def form_invalid(self, form):
        username = self.request.POST.get('username', '')
        cache_key = get_cache_key(username, self.get_client_ip())
        attempts = cache.get(cache_key, 0) + 1
        cache.set(cache_key, attempts, BLOCK_TIME)
        self.request.session[SESSION_FLAG] = attempts >= MAX_ATTEMPTS
        return super().form_invalid(form)