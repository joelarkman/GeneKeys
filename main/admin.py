from django.contrib import admin
from .models import Panel, Gene, Transcript, PanelGene, GeneKey

# Register your models here.
# Each model has been modified to allow read only fields to be viewed and saved within the admin view.


class PanelAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
    search_fields = ['name']

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()


admin.site.register(Panel, PanelAdmin)


class GeneAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
    ordering = ['-added_at']
    search_fields = ['name']

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()


admin.site.register(Gene, GeneAdmin)

class TranscriptAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
    search_fields = ['name']
    ordering = ['-added_at']
    autocomplete_fields = ['Gene']

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()

admin.site.register(Transcript, TranscriptAdmin)

class PanelGeneAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
    autocomplete_fields = ['panel', 'gene', 'transcript']

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()


admin.site.register(PanelGene, PanelGeneAdmin)


class GeneKeyAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()


admin.site.register(GeneKey, GeneKeyAdmin)
