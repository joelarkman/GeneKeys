from django.contrib import admin
from .models import Panel, Gene, Transcript, PanelGene, GeneKey
from django.utils.safestring import mark_safe
from django.urls import reverse

# Register your models here.
# Each model has been modified to allow read only fields to be viewed and saved within the admin view.


class PanelGeneInline(admin.TabularInline):
    model = PanelGene
    readonly_fields = ('preferred_transcript', 'added_by', 'added_at',
                       'modified_by', 'modified_at')
    autocomplete_fields = ['gene']
    search_fields = ['panel__name', 'gene__name']
    extra = 1


class PanelAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
    search_fields = ['name']
    inlines = [PanelGeneInline]

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for entry in formset.deleted_objects:
            entry.delete()
        for instance in instances:
            if not instance.added_by:
                instance.added_by = request.user
            instance.modified_by = request.user
            if Transcript.objects.filter(Gene=instance.gene, use_by_default=True).count() > 0:
                instance.preferred_transcript = Transcript.objects.get(
                    Gene=instance.gene, use_by_default=True)
            instance.save()
        formset.save_m2m()


"""         for f in formset.forms:
            obj = f.instance
            if Transcript.objects.filter(Gene=obj.gene, use_by_default=True).count() > 0:  
                if obj.transcript != Transcript.objects.get(Gene=obj.gene, use_by_default=True):
                    obj.transcript = Transcript.objects.get(
                        Gene=obj.gene, use_by_default=True)
                    obj.save()
 """

admin.site.register(Panel, PanelAdmin)


class TranscriptInline(admin.TabularInline):
    model = Transcript
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
    search_fields = ['name']
    ordering = ['-added_at']
    autocomplete_fields = ['Gene']
    extra = 1

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()


class GeneAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
    ordering = ['-added_at']
    search_fields = ['name']
    inlines = [TranscriptInline]

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for entry in formset.deleted_objects:
            entry.delete()
        for instance in instances:
            if not instance.added_by:
                instance.added_by = request.user
            instance.modified_by = request.user
            instance.save()
        formset.save_m2m()


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

""" class PanelGeneAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
    autocomplete_fields = ['panel', 'gene', 'transcript']
    search_fields = ['panel__name','gene__name']

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()
admin.site.register(PanelGene, PanelGeneAdmin) """


class GeneKeyAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()


admin.site.register(GeneKey, GeneKeyAdmin)
