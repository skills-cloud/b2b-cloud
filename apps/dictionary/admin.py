from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from adminsortable2.admin import SortableAdminMixin

from dictionary import models as dictionary_models


class DictionaryBaseAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'name', 'is_verified']
    list_editable = ['name', 'is_verified']
    list_filter = ['is_verified']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(dictionary_models.TypeOfEmployment)
class TypeOfEmploymentAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.Country)
class CountryAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.City)
class CityAdmin(DictionaryBaseAdmin):
    list_display = DictionaryBaseAdmin.list_display + ['country']
    list_filter = DictionaryBaseAdmin.list_filter + ['country']
    autocomplete_fields = ['country']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('country')


@admin.register(dictionary_models.Citizenship)
class CitizenshipAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.ContactType)
class ContactTypeAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.EducationPlace)
class EducationPlaceAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.EducationSpecialty)
class EducationSpecialtyAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.EducationGraduate)
class EducationGraduateAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.Position)
class PositionAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.PhysicalLimitation)
class PhysicalLimitationAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.IndustrySector)
class IndustrySectorAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.Competence)
class CompetenceAdmin(DraggableMPTTAdmin):
    search_fields = ['name']
    mptt_level_indent = 10
    list_display = ['tree_actions', 'indented_title', 'is_verified']
    list_display_links = ['indented_title']
    list_filter = ['is_verified']
