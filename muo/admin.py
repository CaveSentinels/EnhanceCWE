from django.contrib import admin
from models import *


class TagAdmin(admin.ModelAdmin):
    fields = ['name']
    search_fields = ['name']


class OSRAdmin(admin.ModelAdmin):
    fields = ['description', 'use_case', 'tags']
    search_fields = ['description', 'tags__name']


class OSRAdminInline(admin.TabularInline):
    model = OSR
    extra = 1
    fields = ['description', 'tags']


class UseCaseAdmin(admin.ModelAdmin):
    fields = ['misuse_case', 'description', 'tags']
    inlines = [OSRAdminInline]


class UseCaseAdminInLine(admin.TabularInline):
    model = UseCase
    extra = 1
    fields = ['description', 'tags']


class MisuseCaseAdmin(admin.ModelAdmin):
    fields = ['cwes', 'description', 'tags']
    inlines = [UseCaseAdminInLine]


admin.site.register(Tag, TagAdmin)
admin.site.register(MisuseCase, MisuseCaseAdmin)
admin.site.register(UseCase, UseCaseAdmin)
admin.site.register(OSR, OSRAdmin)
