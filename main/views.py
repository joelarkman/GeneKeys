from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.template.loader import render_to_string

from .forms import AddKeyForm, KeyCommentForm, PanelGeneForm
from .models import Gene, GeneKey, Panel, PanelGene, Transcript


def home(request):
    panels = Panel.objects.all()

    context = {
        'panels': panels
    }

    return render(request, 'main/home.html', context)


def panel_keys(request, pk):
    panel = get_object_or_404(Panel, pk=pk)
    active_gene_keys = GeneKey.objects.filter(
        panel=pk).exclude(archived=True).exclude(checked=False)
    archived_gene_keys = GeneKey.objects.filter(
        panel=pk).exclude(archived=False).exclude(checked=False)
    panel_genes = PanelGene.objects.filter(panel=pk)

    context = {
        'title': panel.name,
        'panel': panel,
        'active_gene_keys': active_gene_keys,
        'archived_gene_keys': archived_gene_keys,
        'panel_genes': panel_genes
    }

    return render(request, 'main/panel_keys.html', context)


@login_required
def add_key(request, pk):
    panel = get_object_or_404(Panel, pk=pk)
    user = request.user  # Fix this

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
        'panel': panel
    }

    return render(request, 'main/add_key.html', context)


def load_genes(request):
    panel_id = request.GET.get('panel')
    genes = Panel.objects.get(pk=panel_id).genes.all()
    return render(request, 'main/genes_dropdown_list_options.html', {'genes': genes})


def key_archive(request, pk, key):
    user = request.user
    panel = get_object_or_404(Panel, pk=pk)
    key = get_object_or_404(GeneKey, pk=key)
    data = dict()
    if request.method == 'POST':
        key.archived = True
        key.archived_by = user
        key.archived_at = datetime.now()
        key.save()
        # This is just to play along with the existing code
        data['form_is_valid'] = True
        active_gene_keys = GeneKey.objects.filter(
            panel=panel.id).exclude(archived=True).exclude(checked=False)
        archived_gene_keys = GeneKey.objects.filter(
            panel=panel.id).exclude(archived=False).exclude(checked=False)
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


def save_panel_gene_form(request, form, template_name, pk, panel_gene):
    panel = get_object_or_404(Panel, pk=pk)
    panel_gene = get_object_or_404(PanelGene, id=panel_gene)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            panel_genes = PanelGene.objects.filter(panel=pk)
            data['html_panel_gene_list'] = render_to_string('main/includes/partial_panel_gene_list.html', {
                'panel': panel,
                'panel_gene': panel_gene,
                'panel_genes': panel_genes
            })
        else:
            data['form_is_valid'] = False
    context = {'panel': panel,
               'panel_gene': panel_gene,
               'form': form}
    data['html_form'] = render_to_string(
        template_name, context, request=request)
    return JsonResponse(data)


def panel_gene_edit(request, pk, panel_gene):
    item = get_object_or_404(PanelGene, id=panel_gene)
    if request.method == 'POST':
        form = PanelGeneForm(request.POST, instance=item)
        form.fields['transcript'].queryset = Transcript.objects.filter(
            Gene=item.gene.id)
    else:
        form = PanelGeneForm(instance=item)
        form.fields['transcript'].queryset = Transcript.objects.filter(
            Gene=item.gene.id)
    return save_panel_gene_form(request, form, 'main/includes/partial_panel_gene_edit.html', pk, panel_gene)


def save_key_comment_form(request, form, template_name, pk, key):
    panel = get_object_or_404(Panel, pk=pk)
    key = get_object_or_404(GeneKey, pk=key)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            active_gene_keys = GeneKey.objects.filter(
                panel=panel.id).exclude(archived=True).exclude(checked=False)
            data['html_key_list_active'] = render_to_string('main/includes/partial_key_list_active.html', {
                'panel': panel,
                'active_gene_keys': active_gene_keys,
                'key': key
            })
        else:
            data['form_is_valid'] = False
    context = {'panel': panel,
               'key': key,
               'form': form}
    data['html_form'] = render_to_string(
        template_name, context, request=request)
    return JsonResponse(data)


def key_comment(request, pk, key):

    instance = get_object_or_404(GeneKey, pk=key)
    if request.method == 'POST':
        form = KeyCommentForm(request.POST, instance=instance)
    else:
        form = KeyCommentForm(instance=instance)
    return save_key_comment_form(request, form, 'main/includes/partial_key_comment.html', pk, key)


@login_required
def pending_keys(request, pk):
    panel = get_object_or_404(Panel, pk=pk)
    pending_gene_keys = GeneKey.objects.all().exclude(checked=True)

    context = {
        'title': 'Pending Keys',
        'panel': panel,
        'pending_gene_keys': pending_gene_keys
    }

    return render(request, 'main/pending_keys.html', context)


def key_accept(request, pk, key):
    user = request.user
    panel = get_object_or_404(Panel, pk=pk)
    key = get_object_or_404(GeneKey, pk=key)
    data = dict()
    if request.method == 'POST':
        key.checked = True
        key.checked_by = user
        key.checked_at = datetime.now()
        key.save()
        # This is just to play along with the existing code
        data['form_is_valid'] = True
        pending_gene_keys = GeneKey.objects.all().exclude(checked=True)
        data['html_key_list_pending'] = render_to_string('main/includes/partial_key_list_pending.html', {
            'panel': panel,
            'pending_gene_keys': pending_gene_keys,
        })
    else:
        context = {
            'panel': panel,
            'key': key}
        data['html_form'] = render_to_string(
            'main/includes/partial_key_accept.html', context, request=request)
    return JsonResponse(data)
