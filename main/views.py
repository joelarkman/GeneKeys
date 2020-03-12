from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
from django.contrib.auth.models import User

from .models import Panel, GeneKey, PanelGene, Gene
from .forms import AddKeyForm


def home(request):
    panels = Panel.objects.all()

    context = {
        'panels': panels
    }

    return render(request, 'main/home.html', context)


def panel_keys(request, pk):
    panel = get_object_or_404(Panel, pk=pk)
    active_gene_keys = GeneKey.objects.filter(panel=pk).exclude(archived=True)
    archived_gene_keys = GeneKey.objects.filter(
        panel=pk).exclude(archived=False)
    panel_genes = PanelGene.objects.filter(panel=pk)

    context = {
        'title': panel.name,
        'panel': panel,
        'active_gene_keys': active_gene_keys,
        'archived_gene_keys': archived_gene_keys,
        'panel_genes': panel_genes
    }

    return render(request, 'main/panel_keys.html', context)


def add_key(request, pk):
    panel = get_object_or_404(Panel, pk=pk)
    user = User.objects.first()  # Fix this

    if request.method == 'POST':
        form = AddKeyForm(request.POST)
        if form.is_valid():
            genekey = form.save(commit=False)
            #genekey.panel = panel
            genekey.added_by = user
            genekey.save()
            return redirect('panel_keys', pk=panel.pk)
    else:
        form = AddKeyForm()

    context = {
        'title': 'Add key',
        'form': form,
    }

    return render(request, 'main/add_key.html', context)
