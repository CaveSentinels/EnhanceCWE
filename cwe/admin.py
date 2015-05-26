from django.contrib import admin
from models import *

class CategoryAdmin(admin.ModelAdmin):
    fields = ['name']
    search_fields = ['name']


class KeywordAdmin(admin.ModelAdmin):
    fields = ['name']
    search_fields = ['name']


class CWEAdmin(admin.ModelAdmin):
    model = CWE
    fieldsets = [
        ('CWE',            {'fields': ['code', 'name']}),
        ('Categories',  {'fields': ['categories']}),
        ('Keywords',  {'fields': ['keywords'],
                       'classes': ['collapse']}),
    ]
    search_fields = ['name', 'code', 'categories__name', 'keywords__name']
    list_filter = ['categories', 'keywords']


admin.site.register(CWE, CWEAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Keyword, KeywordAdmin)
