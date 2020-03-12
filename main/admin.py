from django.contrib import admin
from .models import Panel, Gene, Transcript, PanelGene, GeneKey
# Register your models here.

admin.site.register(Panel)
admin.site.register(Gene)
admin.site.register(Transcript)
admin.site.register(PanelGene)
admin.site.register(GeneKey)
