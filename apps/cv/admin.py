from django.contrib import admin

from cv import models as cv_models


class CvBaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

