from adminsortable2.admin import SortableAdminMixin
from mptt.admin import DraggableMPTTAdmin

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render

from django.http.response import HttpResponseRedirect


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


@admin.register(dictionary_models.Organization)
class OrganizationAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.Competence)
class CompetenceAdmin(DraggableMPTTAdmin):
    search_fields = ['name']
    mptt_level_indent = 10
    list_display = ['tree_actions', 'indented_title', 'is_verified']
    list_display_links = ['indented_title']
    list_filter = ['is_verified']
    autocomplete_fields = ['parent']
    change_list_template = 'admin/duplicate_button.html'

    def get_duplicate_view(self, request):
        duplicates = []
        competences = dictionary_models.Competence.objects.all()
        for item in competences:
            if dictionary_models.Competence.objects.filter(
                    name__iexact=item.name
            ).count() > 1:
                duplicates.append(item)

        return render(request, 'admin/duplicate_delete_confirm.html',
                      context={'context': duplicates})

    def delete_duplicates_view(self, request):
        competences = dictionary_models.Competence.objects.all()
        for item in competences:
            if dictionary_models.Competence.objects.filter(
                    name__iexact=item.name
            ).count() > 1:
                dupls = dictionary_models.Competence.objects.filter(
                    name__iexact=item.name
                )
                for element in dupls[1:]:
                    dictionary_models.Competence.objects.get(id=element.id).delete()
        return HttpResponseRedirect(
            reverse('admin:dictionary_competence_changelist')
        )

    def get_urls(self):
        urlpatters = super().get_urls()
        urlpatters += [
            path('get-duplicates', self.get_duplicate_view,
                 name='get_duplicates'),
            path('delete-duplicates', self.delete_duplicates_view,
                 name='delete_duplicates')
        ]
        return urlpatters


@admin.register(dictionary_models.Category)
class CategoryAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.Certificate)
class CertificateAdmin(DictionaryBaseAdmin):
    pass


@admin.register(dictionary_models.CurrencyReference)
class CurrencyAdmin(DictionaryBaseAdmin):
    pass

