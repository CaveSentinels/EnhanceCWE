from django.contrib import admin
from base.admin import BaseAdmin
from models import *
import autocomplete_light

@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    fields = ['name']
    search_fields = ['name']


@admin.register(Keyword)
class KeywordAdmin(BaseAdmin):
    fields = ['name']
    search_fields = ['name']


@admin.register(CWE)
class CWEAdmin(BaseAdmin):
    model = CWE
    form = autocomplete_light.modelform_factory(CWE, fields="__all__")
    fieldsets = [
        ('CWE', {'fields': ['code', 'name'],
                 'classes': ['box-col-md-12']}),

        ('Categories', {'fields': ['categories'],
                   'classes': ['box-col-md-6']}),

        ('keywords', {'fields': ['keywords'],
                   'classes': ['box-col-md-6']}),
    ]
    search_fields = ['name', 'code', 'categories__name', 'keywords__name']
    list_filter = ['categories', 'keywords', ('created_by', admin.RelatedOnlyFieldListFilter)]
    date_hierarchy = 'created_at'
