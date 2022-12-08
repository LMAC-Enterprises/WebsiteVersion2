from django.contrib import admin


# Register your models here.
from staticContentApp.models import StaticContentModel


class StaticContentAdmin(admin.ModelAdmin):
    fieldsets = [
         ('Publishing information', {'fields': ['content_id', 'is_enabled', 'is_home_page', 'created_date']}),
         ('Content', {'fields': ['title', 'body']})
    ]


admin.site.register(StaticContentModel, StaticContentAdmin)
