from django.contrib import admin
import nested_admin
from mptt.admin import DraggableMPTTAdmin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from reversion.admin import VersionAdmin
from admin_auto_filters.filters import AutocompleteFilter

from cv.admin import CvAdminFilter
from main import models as main_models


class MainBaseAdmin(VersionAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


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


class OrganizationProjectAdminFilter(AutocompleteFilter):
    title = main_models.OrganizationProject._meta.verbose_name
    field_name = 'organization_project'


@admin.register(main_models.Project)
class ProjectAdmin(MainBaseAdmin):
    autocomplete_fields = ['resource_managers', 'recruiters']


@admin.register(main_models.RequestType)
class RequestTypeAdmin(MainBaseAdmin):
    readonly_fields = []


@admin.register(main_models.Request)
class RequestAdmin(VersionAdmin, nested_admin.NestedModelAdmin):
    class TypeFilter(AutocompleteFilter):
        title = main_models.Request._meta.get_field('type').verbose_name
        field_name = 'type'

    class ProjectFilter(AutocompleteFilter):
        title = main_models.Request._meta.get_field('project').verbose_name
        field_name = 'project'

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
            autocomplete_fields = ['cv', 'organization_project_card_items']

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
        'id_verbose', 'requirements_count', 'status', 'priority', 'type', 'organization_project', 'project',
        'deadline_date', 'created_at', 'updated_at',
    ]
    list_filter = [
        'priority',
        'status',
        OrganizationProjectAdminFilter,
        TypeFilter,
        IndustrySectorFilter,
        ProjectFilter,
        ['deadline_date', DateRangeFilter],
        ['created_at', DateTimeRangeFilter],
        ['updated_at', DateTimeRangeFilter],
    ]
    autocomplete_fields = [
        'type', 'industry_sector', 'organization_project', 'project', 'resource_manager', 'recruiter'
    ]
    search_fields = ['id', 'description']
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            *main_models.Request.objects.get_queryset_prefetch_related()
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
