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


@admin.register(main_models.Organization, main_models.OrganizationCustomer)
class OrganizationAdmin(MainBaseAdmin):
    class OrganizationContractorFilter(OrganizationAdminFilter):
        model_queryset = main_models.OrganizationContractor.objects
        title = main_models.Organization._meta.get_field('contractor').verbose_name
        lookup_field = 'contractor'
        parameter_name = 'contractor'

    list_filter = ['is_customer', 'is_contractor', OrganizationContractorFilter]
    list_display = MainBaseAdmin.list_display + ['contractor', 'is_customer', 'is_contractor', ]
    autocomplete_fields = ['contractor']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('contractor')


@admin.register(main_models.OrganizationContractor)
class OrganizationContractorAdmin(OrganizationAdmin):
    class UserRoleInline(admin.TabularInline):
        model = main_models.OrganizationContractorUserRole
        autocomplete_fields = ['user']
        extra = 0

    inlines = [
        UserRoleInline
    ]


@admin.register(main_models.OrganizationProject)
class OrganizationProjectAdmin(MainBaseAdmin):
    class UserRoleInline(admin.TabularInline):
        model = main_models.OrganizationProjectUserRole
        autocomplete_fields = ['user']
        extra = 0

    inlines = [
        UserRoleInline
    ]
    list_display = ['id', 'organization_customer', 'name']
    list_filter = ['organization_customer', 'industry_sector']
    autocomplete_fields = ['organization_customer', 'industry_sector', 'manager', ]

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
