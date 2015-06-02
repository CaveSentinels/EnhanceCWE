from .models import *


class CWEAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^code', 'name']
    attrs = {'placeholder': 'CWE...'}
    model = CWE
    widget_attrs = {
        'class': 'modern-style',
    }


autocomplete_light.register(CWEAutocomplete)


class CategoryAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    attrs = {'placeholder': 'categories...'}
    model = Category
    widget_attrs = {
        'class': 'modern-style',
    }


autocomplete_light.register(CategoryAutocomplete)


class KeywordAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    attrs = {'placeholder': 'keywords...'}
    model = Keyword
    widget_attrs = {
        'class': 'modern-style',
    }


autocomplete_light.register(KeywordAutocomplete)
