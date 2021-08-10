from django.contrib import admin
import nested_admin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from mptt.admin import TreeRelatedFieldListFilter
from reversion.admin import VersionAdmin
from admin_auto_filters.filters import AutocompleteFilter

from cv import models as cv_models


@admin.register(cv_models.CV)
class CvAdmin(VersionAdmin, nested_admin.NestedModelAdmin):
    class CountryFilter(AutocompleteFilter):
        title = cv_models.CV._meta.get_field('country').verbose_name
        field_name = 'country'

    class CityFilter(AutocompleteFilter):
        title = cv_models.CV._meta.get_field('city').verbose_name
        field_name = 'city'

    class CitizenshipFilter(AutocompleteFilter):
        title = cv_models.CV._meta.get_field('citizenship').verbose_name
        field_name = 'citizenship'

    class CvContactInline(nested_admin.NestedTabularInline):
        model = cv_models.CvContact
        autocomplete_fields = ['contact_type']
        extra = 0

    class CvTimeSlotInline(nested_admin.NestedTabularInline):
        model = cv_models.CvTimeSlot
        autocomplete_fields = ['country', 'city', 'type_of_employment']
        extra = 0

    class CvPositionInline(nested_admin.NestedTabularInline):
        class CvPositionFileInline(nested_admin.NestedTabularInline):
            model = cv_models.CvPositionFile
            extra = 0
        inlines = [CvPositionFileInline]
        model = cv_models.CvPosition
        autocomplete_fields = ['position', 'competencies']
        extra = 0

    class CvCareerInline(nested_admin.NestedTabularInline):
        class CvCareerFileInline(nested_admin.NestedTabularInline):
            model = cv_models.CvCareerFile
            extra = 0
        inlines = [CvCareerFileInline]
        model = cv_models.CvCareer
        autocomplete_fields = ['organization', 'position', 'competencies', 'projects']
        extra = 0

    class CvEducactionInline(nested_admin.NestedTabularInline):
        model = cv_models.CvEducation
        autocomplete_fields = ['education_place', 'education_speciality', 'education_graduate', 'competencies']
        extra = 0

    class CvCertificatenInline(nested_admin.NestedTabularInline):
        model = cv_models.CvCertificate
        autocomplete_fields = ['education_place', 'education_speciality', 'education_graduate', 'competencies']
        extra = 0

    inlines = [
        CvContactInline,
        CvTimeSlotInline,
        CvPositionInline,
        CvCareerInline,
        CvEducactionInline,
        CvCertificatenInline,
    ]
    list_select_related = True
    list_display = ['id', 'last_name', 'first_name', 'middle_name', 'user', 'created_at', 'updated_at']
    list_filter = [
        'gender', 'is_verified', 'is_with_disabilities', 'is_resource_owner',
        CountryFilter, CityFilter, CitizenshipFilter,
        ['birth_date', DateRangeFilter],
        ['competencies', TreeRelatedFieldListFilter],
        ['created_at', DateTimeRangeFilter],
        ['updated_at', DateTimeRangeFilter],
    ]
    autocomplete_fields = ['user', 'country', 'city', 'citizenship', 'competencies']
    search_fields = ['first_name', 'last_name', 'middle_name']
    readonly_fields = ['created_at', 'updated_at']
