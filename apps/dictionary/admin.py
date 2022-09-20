from adminsortable2.admin import SortableAdminMixin
from mptt.admin import DraggableMPTTAdmin

from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render
from django.utils.translation import gettext as _

from django.http.response import HttpResponseRedirect, JsonResponse

from dictionary import models as dictionary_models
from cv import models as cv_models


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
    change_list_template = 'admin/contacts/change_list.html'

    class Media:
        js = (
            'js/contact-type-optimizer.js',
        )
        css = {
            'all': (
                'styles/contact-type-optimizer.css',
            )
        }

    def move_email_contact_type(self, request):
        return self._move_email_contact_type(request)

    def _move_email_contact_type(self, request):
        e_mail_type = self.model.objects.filter(name__iexact='e-mail').first()
        email_types = self.model.objects.filter(name__iexact='email')

        if not email_types.exists():
            return JsonResponse({
                'message': _('Contact type with name `Email` not found!')
            }, status=400)

        if not e_mail_type:
            e_mail_type = self.model.objects.create(name='e-mail')

        cvs = cv_models.CV.objects.filter(
            contacts__contact_type__in=email_types
        )

        for cv in cvs:
            email_contact_items = cv.contacts.filter(
                contact_type__in=email_types
            )
            if cv.contacts.filter(contact_type=e_mail_type).exists():
                email_contact_items.delete()
                continue

            new_e_mail_items = [
                cv_models.CvContact(
                    cv=cv,
                    contact_type=e_mail_type,
                    value=x.value,
                    is_primary=x.is_primary,
                    comment=x.comment
                ) for x in email_contact_items
            ]
            cv_models.CvContact.objects.bulk_create(new_e_mail_items)
            email_contact_items.delete()

        email_types.delete()

        return JsonResponse({
            'message': _('Contact types successfully optimized!'),
        })

    def get_urls(self):
        urlpatterns = [
            path('move-email-contact-type/',
                 self.admin_site.admin_view(self.move_email_contact_type),
                 name='move_email_contact_type')
        ]
        urlpatterns += super().get_urls()
        return urlpatterns


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

