from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from project.contrib.admin_tools.filter import ModelAutocompleteFilter
from main import models as main_models
from main.admin.base import MainBaseAdmin


class OrganizationProjectAdminFilter(ModelAutocompleteFilter):
    title = main_models.OrganizationProject._meta.verbose_name
    model_queryset = main_models.OrganizationProject.objects
    model_search_fields = ['name__icontains']
    lookup_field = 'organization_project'
    parameter_name = 'project'


class OrganizationAdminFilter(ModelAutocompleteFilter):
    title = main_models.Organization._meta.verbose_name
    model_queryset = main_models.Organization.objects
    model_search_fields = ['name__icontains']
    lookup_field = 'organization'
    parameter_name = 'organization'


@admin.register(main_models.Organization)
class OrganizationAdmin(MainBaseAdmin):
    list_filter = ['is_customer']
    list_display = MainBaseAdmin.list_display + list_filter


@admin.register(main_models.OrganizationProject)
class OrganizationProjectAdmin(MainBaseAdmin):
    list_display = ['id', 'organization', 'name']
    list_filter = ['organization', 'industry_sector']
    autocomplete_fields = ['organization', 'industry_sector', 'manager', 'resource_managers', 'recruiters']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            *main_models.OrganizationProject.objects.get_queryset_prefetch_related()
        )


@admin.register(main_models.OrganizationProjectCardItemTemplate)
class OrganizationProjectCardItemTemplateAdmin(DraggableMPTTAdmin):
    search_fields = ['name', 'description']
    mptt_level_indent = 10
    list_display = ['tree_actions', 'indented_title', 'description']
    list_display_links = ['indented_title']
    autocomplete_fields = ['positions']


@admin.register(main_models.OrganizationProjectCardItem)
class OrganizationProjectCardItemAdmin(OrganizationProjectCardItemTemplateAdmin):
    list_display = OrganizationProjectCardItemTemplateAdmin.list_display + ['organization_project']
    list_filter = [OrganizationProjectAdminFilter]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('organization_project')
