from django.contrib import admin
from django.db import transaction
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Gene, GeneKey, Panel, PanelGene, Transcript

# Register your models here.
# Each model has been modified to allow read only fields to be viewed and saved within the admin view.

admin.site.site_title = 'WMRGL Gene Keys'
admin.site.site_header = 'WMRGL Gene Keys Administration'
admin.site.index_title = 'App administration'


class PanelGeneInline(admin.TabularInline):
    model = PanelGene
    verbose_name_plural = 'Existing Genes on Panel'
    readonly_fields = ('gene','preferred_transcript', 'added_by', 'added_at',
                       'modified_by', 'modified_at')
    extra = 1
    max_num = 0
    show_change_link = True

class AddPanelGeneInline(admin.TabularInline):
    model = PanelGene
    verbose_name_plural = 'Add Gene to Panel'
    fields = ('gene',)
    can_delete = False
    autocomplete_fields = ['gene']
    extra = 1

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return  queryset.none() 


class PanelAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
    search_fields = ['name']
    inlines = [PanelGeneInline,AddPanelGeneInline]

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
            if Transcript.objects.filter(Gene=instance.gene, use_by_default=True).count() == 1:
                instance.preferred_transcript = Transcript.objects.get(
                    Gene=instance.gene, use_by_default=True)
            instance.save()
        formset.save_m2m()


admin.site.register(Panel, PanelAdmin)


class TranscriptInline(admin.TabularInline):
    model = Transcript
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
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

            # This code ensures only one transcript can be set as default (for each gene).
            # It also sets a newly added transcript to default if there is no current default.
            if not instance.use_by_default:
                if Transcript.objects.filter(Gene=instance.Gene, use_by_default=True).count() == 0:
                    instance.use_by_default = True
                return instance.save()
            with transaction.atomic():
                Transcript.objects.filter(Gene=instance.Gene).filter(
                    use_by_default=True).update(use_by_default=False)
                return instance.save()

        formset.save_m2m()


admin.site.register(Gene, GeneAdmin)


class GeneKeyAdmin(admin.ModelAdmin):
    readonly_fields = ('added_by', 'added_at', 'modified_by', 'modified_at')
    search_fields = ['key']

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()


admin.site.register(GeneKey, GeneKeyAdmin)


""" class TranscriptAdmin(admin.ModelAdmin):
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
    autocomplete_fields = ['panel', 'gene', 'preferred_transcript']
    search_fields = ['panel__name','gene__name']

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.modified_by = request.user
        obj.save()
admin.site.register(PanelGene, PanelGeneAdmin) """