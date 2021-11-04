import nested_admin
from django.contrib import admin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from reversion.admin import VersionAdmin
from admin_auto_filters.filters import AutocompleteFilter

from cv.admin import CvAdminFilter
from main import models as main_models
from main.admin.module import ModuleAdminFilter
from main.admin.base import MainBaseAdmin
from main.admin.organization import OrganizationProjectAdminFilter, OrganizationAdminFilter

__all__ = []


@admin.register(main_models.RequestType)
class RequestTypeAdmin(MainBaseAdmin):
    readonly_fields = []


@admin.register(main_models.Request)
class RequestAdmin(VersionAdmin, nested_admin.NestedModelAdmin):
    class OrganizationFilter(OrganizationAdminFilter):
        lookup_field = 'module__organization_project__organization'

    class OrganizationProjectFilter(OrganizationProjectAdminFilter):
        lookup_field = 'module__organization_project'

    class TypeFilter(AutocompleteFilter):
        title = main_models.Request._meta.get_field('type').verbose_name
        field_name = 'type'

    class IndustrySectorFilter(AutocompleteFilter):
        title = main_models.Request._meta.get_field('industry_sector').verbose_name
        field_name = 'industry_sector'

    class RequestRequirementInline(nested_admin.NestedTabularInline):
        class RequestRequirementCompetenceInline(nested_admin.NestedTabularInline):
            model = main_models.RequestRequirementCompetence
            extra = 0
            autocomplete_fields = ['competence']

        class RequestRequirementCvInline(nested_admin.NestedTabularInline):
            model = main_models.RequestRequirementCv
            readonly_fields = ['created_at', 'updated_at']
            extra = 0
            autocomplete_fields = ['cv']

        inlines = [
            RequestRequirementCompetenceInline,
            RequestRequirementCvInline,
        ]
        model = main_models.RequestRequirement
        autocomplete_fields = ['position', 'type_of_employment', 'work_location_city']
        extra = 0

    inlines = [
        RequestRequirementInline,
    ]
    list_display = [
        'id_verbose', '_organization', '_organization_project', 'module', 'requirements_count', 'status', 'priority',
        'type',     'deadline_date', 'created_at', 'updated_at',
    ]
    list_filter = [
        'priority',
        'status',
        OrganizationFilter,
        OrganizationProjectFilter,
        ModuleAdminFilter,
        TypeFilter,
        IndustrySectorFilter,
        ['deadline_date', DateRangeFilter],
        ['created_at', DateTimeRangeFilter],
        ['updated_at', DateTimeRangeFilter],
    ]
    autocomplete_fields = [
        'type', 'industry_sector', 'module', 'resource_manager', 'recruiter'
    ]
    search_fields = ['id', 'description']
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            *main_models.Request.objects.get_queryset_prefetch_related()
        )

    def _organization_project(self, instance):
        return instance.module.organization_project.name

    _organization_project.short_description = OrganizationProjectAdminFilter.title
    _organization_project.admin_order_field = 'module__organization_project'

    def _organization(self, instance):
        return instance.module.organization_project.organization.name

    _organization.short_description = OrganizationAdminFilter.title
    _organization.admin_order_field = 'module__organization_project__organization_id'


@admin.register(main_models.TimeSheetRow)
class TimeSheetRowAdmin(admin.ModelAdmin):
    class RequestFilter(AutocompleteFilter):
        title = main_models.TimeSheetRow._meta.get_field('request').verbose_name
        field_name = 'request'

    list_display = ['id', 'task_name', 'request', 'cv', 'task_name', 'task_description']
    search_fields = ['task_name', 'task_description']
    autocomplete_fields = ['request', 'cv']
    list_filter = [RequestFilter, CvAdminFilter]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            *main_models.TimeSheetRow.objects.get_queryset_prefetch_related()
        )
