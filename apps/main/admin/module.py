import nested_admin
from django.contrib import admin
from reversion.admin import VersionAdmin

from project.contrib.admin_tools.filter import ModelAutocompleteFilter
from main import models as main_models
from main.admin.organization import OrganizationAdminFilter, OrganizationProjectAdminFilter


class ModuleAdminFilter(ModelAutocompleteFilter):
    title = main_models.Module._meta.verbose_name
    model_queryset = main_models.Module.objects
    model_search_fields = ['name__icontains']
    lookup_field = 'module'
    parameter_name = 'module'


@admin.register(main_models.FunPointTypeDifficultyLevel)
class FunPointDifficultyLevelAdmin(admin.ModelAdmin):
    """
    Для автозавершения в админке.
    Скрыто CSS'ом
    """
    search_fields = ['fun_point_type__name', 'name']


@admin.register(main_models.FunPointType)
class FunPointTypeAdmin(VersionAdmin, nested_admin.NestedModelAdmin):
    class FunPointDifficultyLevelInline(nested_admin.NestedTabularInline):
        model = main_models.FunPointTypeDifficultyLevel
        extra = 0

    class FunPointTypePositionLaborEstimateInline(nested_admin.NestedTabularInline):
        model = main_models.FunPointTypePositionLaborEstimate
        extra = 0
        autocomplete_fields = ['position']

    inlines = [
        FunPointDifficultyLevelInline,
        FunPointTypePositionLaborEstimateInline,
    ]

    list_display = ['id', '_organization', 'name']
    list_display_links = ['id', 'name']
    autocomplete_fields = ['organization_customer']
    search_fields = ['name']
    list_filter = [
        OrganizationAdminFilter,
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            *self.model.objects.get_queryset_prefetch_related()
        )

    def _organization(self, instance):
        if not instance.organization_customer:
            return
        return instance.organization_customer.name

    _organization.short_description = OrganizationAdminFilter.title
    _organization.admin_order_field = 'organization_customer_id'


@admin.register(main_models.Module)
class ModuleAdmin(VersionAdmin, nested_admin.NestedModelAdmin):
    class OrganizationFilter(OrganizationAdminFilter):
        parameter_name = 'organization'
        field_name = 'organization_project__organization_id'

    class FunPointInline(nested_admin.NestedTabularInline):
        model = main_models.ModuleFunPoint
        autocomplete_fields = ['fun_point_type', 'difficulty_level']
        extra = 0

    class PositionLaborEstimateInline(nested_admin.NestedTabularInline):
        model = main_models.ModulePositionLaborEstimate
        autocomplete_fields = ['position']
        extra = 0

    inlines = [
        FunPointInline,
        PositionLaborEstimateInline,
    ]
    list_display = ['id', '_organization', 'organization_project', 'name', ]
    autocomplete_fields = ['organization_project']
    list_filter = [
        OrganizationFilter,
        OrganizationProjectAdminFilter,
    ]
    search_fields = ['name', 'organization_project__name', 'organization_project__organization_customer__name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            *self.model.objects.get_queryset_prefetch_related()
        )

    def _organization(self, instance):
        return instance.organization_project.organization_customer.name

    _organization.short_description = OrganizationAdminFilter.title
    _organization.admin_order_field = 'organization_project__organization_customer_id'
