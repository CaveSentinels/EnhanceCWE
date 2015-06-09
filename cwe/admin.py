from django import forms
from django.contrib import admin
from base.admin import BaseAdmin
from models import *
import autocomplete_light

@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    fields = ['name']
    search_fields = ['name']


class KeywordAdminForm(forms.ModelForm):
    """
    Creating a custom form for keyword to validate the name is a single word only
    """
    def clean_name(self):
        if len(self.cleaned_data["name"].split()) > 1:
            raise forms.ValidationError("Keyword name should only have a single word")

        """ Check the keyword stemmed format doesn't already exist in the database """
        cwe_search = CWESearchLocator.get_instance()
        stemmed_name = cwe_search.stem_text([self.cleaned_data["name"].lower()])
        if stemmed_name:
            # stem_text() always returns a list. Get the first element
            stemmed_name = stemmed_name[0]
            if Keyword.objects.filter(name__exact=stemmed_name).exists():
                raise forms.ValidationError("Keyword stemmed name (%s) already exist!" % stemmed_name)
            else:
                self.cleaned_data["name"] = stemmed_name

        return self.cleaned_data["name"]


@admin.register(Keyword)
class KeywordAdmin(BaseAdmin):
    form = KeywordAdminForm
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
