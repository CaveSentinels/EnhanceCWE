from django.contrib import admin
from django_admin_bootstrapped.widgets import GenericContentTypeSelect
from models import *


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ['name']
    search_fields = ['name']


@admin.register(OSR)
class OSRAdmin(admin.ModelAdmin):
    fields = ['description', 'use_case', 'tags']
    search_fields = ['description', 'tags__name']


class OSRAdminInline(admin.TabularInline):
    model = OSR
    extra = 1
    fields = ['description', 'tags']


@admin.register(UseCase)
class UseCaseAdmin(admin.ModelAdmin):
    fields = ['misuse_case', 'description', 'tags']
    inlines = [OSRAdminInline]



class UseCaseAdminInLine(admin.StackedInline):
    model = UseCase
    extra = 1
    fields = ['description', 'tags']


@admin.register(MisuseCase)
class MisuseCaseAdmin(admin.ModelAdmin):
    fields = ['cwes', 'description', 'tags']
    inlines = [UseCaseAdminInLine]

