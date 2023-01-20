from django.contrib import admin


# Register your models here.
from staticContentApp.models import StaticContentModel


class StaticContentAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ('title', 'created_date', 'is_home_page')
    fieldsets = [
         ('Publishing information', {'fields': ['content_id', 'is_enabled', 'is_home_page', 'created_date']}),
         ('Content', {'fields': ['title', 'body']})
    ]

    def is_home_page(self, obj):
        return obj.is_home_page == 1

    is_home_page.boolean = True


admin.site.register(StaticContentModel, StaticContentAdmin)
