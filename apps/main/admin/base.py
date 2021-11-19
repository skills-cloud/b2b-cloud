from reversion.admin import VersionAdmin


class MainBaseAdmin(VersionAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
