from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django.template.loader import render_to_string

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
        form.panel = panel
        if form.is_valid():
            genekey = form.save(commit=False)
            #genekey.panel = panel
            genekey.added_by = user
            genekey.save()
            return redirect('panel_keys', pk=panel.pk)
    else:
        form = AddKeyForm(initial={'panel': pk})

    context = {
        'title': 'Add key',
        'form': form,
    }

    return render(request, 'main/add_key.html', context)


def load_genes(request):
    panel_id = request.GET.get('panel')
    genes = Panel.objects.get(pk=panel_id).genes.all()
    return render(request, 'main/genes_dropdown_list_options.html', {'genes': genes})


def key_archive(request, pk, key):
    panel = get_object_or_404(Panel, pk=pk)
    key = get_object_or_404(GeneKey, pk=key)
    data = dict()
    if request.method == 'POST':
        key.archived = True
        key.save()
        # This is just to play along with the existing code
        data['form_is_valid'] = True
        active_gene_keys = GeneKey.objects.filter(
            panel=panel.id).exclude(archived=True)
        archived_gene_keys = GeneKey.objects.filter(
            panel=panel.id).exclude(archived=False)
        data['html_key_list_active'] = render_to_string('main/includes/partial_key_list_active.html', {
            'panel': panel,
            'active_gene_keys': active_gene_keys,
        })
        data['html_key_list_archived'] = render_to_string('main/includes/partial_key_list_archived.html', {
            'panel': panel,
            'archived_gene_keys': archived_gene_keys,
        })
    else:
        context = {
            'panel': panel,
            'key': key}
        data['html_form'] = render_to_string(
            'main/includes/partial_key_archive.html', context, request=request)
    return JsonResponse(data)
