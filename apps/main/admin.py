from django.contrib import admin

from main import models as main_models


class MainBaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(main_models.Customer)
class CustomerAdmin(MainBaseAdmin):
    pass


@admin.register(main_models.Project)
class ProjectAdmin(MainBaseAdmin):
    pass
