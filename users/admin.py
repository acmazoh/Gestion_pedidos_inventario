from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from .models import Role, UserProfile


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
	list_display = ("id", "name")
	search_fields = ("name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "role", "is_active")
	list_filter = ("role", "is_active")
	search_fields = ("user__username", "user__email", "role__name")


class UserProfileInline(admin.StackedInline):
	model = UserProfile
	can_delete = False
	fk_name = "user"
	extra = 0


class UserAdmin(DjangoUserAdmin):
	inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
