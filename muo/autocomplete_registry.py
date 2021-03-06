from .models import *
import autocomplete_light

class MisuseCaseAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['id', 'name']
    attrs = {'placeholder': 'Misuse Case...'}
    model = MisuseCase
    widget_attrs = {
        'class': 'modern-style',
    }
autocomplete_light.register(MisuseCaseAutocomplete)


class UseCaseAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['id', 'name']
    attrs = {'placeholder': 'Use Case...'}
    model = UseCase
    widget_attrs = {
        'class': 'modern-style',
    }
autocomplete_light.register(UseCaseAutocomplete)


class TagAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^name',]
    attrs = {'placeholder': 'Tag...'}
    model = Tag
    widget_attrs = {
        'class': 'modern-style',
    }
autocomplete_light.register(TagAutocomplete)
