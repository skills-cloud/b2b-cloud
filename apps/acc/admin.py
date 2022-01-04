from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase, GroupAdmin as GroupAdminBase
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.models import Group as GroupBase

from acc import models as acc_models

admin.site.unregister(GroupBase)


@admin.register(acc_models.User)
class UserAdmin(UserAdminBase):
    class UserRoleInline(admin.TabularInline):
        model = acc_models.UserSystemRole
        extra = 0

    inlines = [UserRoleInline]
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('is_active', 'is_staff', 'is_superuser')

    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('password',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                # 'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

# class GroupUserInline(admin.TabularInline):
#     model = acc_models.Group.user_set.through
#     readonly_fields = ['user']
#     extra = 0

# @admin.register(acc_models. Group)
# class GroupAdmin(GroupAdminBase):
#     inlines = [GroupUserInline]
