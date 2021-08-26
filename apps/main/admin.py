from django.contrib import admin
import nested_admin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from reversion.admin import VersionAdmin
from admin_auto_filters.filters import AutocompleteFilter

from main import models as main_models


class MainBaseAdmin(VersionAdmin):
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

    class CustomerFilter(AutocompleteFilter):
        title = main_models.Request._meta.get_field('customer').verbose_name
        field_name = 'customer'

    class ProjectFilter(AutocompleteFilter):
        title = main_models.Request._meta.get_field('project').verbose_name
        field_name = 'project'

    class IndustrySectorFilter(AutocompleteFilter):
        title = main_models.Request._meta.get_field('industry_sector').verbose_name
        field_name = 'industry_sector'

    class RequestRequirementInline(nested_admin.NestedTabularInline):
        class RequestRequirementCompetenceInline(nested_admin.NestedTabularInline):
            autocomplete_fields = ['competence']
            model = main_models.RequestRequirementCompetence
            extra = 0

        inlines = [
            RequestRequirementCompetenceInline,
        ]
        model = main_models.RequestRequirement
        autocomplete_fields = ['position', 'type_of_employment', 'work_location_city']
        extra = 0

    inlines = [
        RequestRequirementInline,
    ]
    list_display = [
        'id_verbose', 'requirements_count', 'status', 'priority', 'type', 'customer', 'project', 'deadline_date',
        'created_at', 'updated_at'
    ]
    list_filter = [
        'priority',
        'status',
        TypeFilter,
        CustomerFilter,
        IndustrySectorFilter,
        ProjectFilter,
        ['deadline_date', DateRangeFilter],
        ['created_at', DateTimeRangeFilter],
        ['updated_at', DateTimeRangeFilter],
    ]
    autocomplete_fields = ['type', 'customer', 'industry_sector', 'project', 'resource_manager', 'recruiter']
    search_fields = ['id', 'description']
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            *main_models.Request.objects.get_queryset_prefetch_related()
        )
