from django.contrib import admin

from main import models as main_models


class MainBaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(main_models.Organization)
class OrganizationAdmin(MainBaseAdmin):
    pass


@admin.register(main_models.OrganizationProject)
class OrganizationProjectAdmin(MainBaseAdmin):
    list_display = ['id', 'organization', 'name']
    list_filter = ['organization']
    autocomplete_fields = ['organization']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('organization')

