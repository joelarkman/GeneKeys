import xlwt
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.template.loader import render_to_string

from .forms import AddKeyForm, KeyCommentForm, PanelGeneForm
from .models import Gene, GeneKey, Panel, PanelGene, Transcript

######################
##### Main Views #####
######################


def home(request):
    panels = Panel.objects.all()

    context = {
        'panels': panels
    }

    return render(request, 'main/home.html', context)


def panel_keys(request, pk):
    panel = get_object_or_404(Panel, pk=pk)
    active_gene_keys = GeneKey.objects.filter(
        panel=pk).exclude(archived=True).exclude(checked=False).order_by('-added_at')
    archived_gene_keys = GeneKey.objects.filter(
        panel=pk).exclude(archived=False).exclude(checked=False).order_by('-added_at')
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
    user = request.user

    if request.method == 'POST':
        form = AddKeyForm(request.POST)
        form.panel = panel
        if form.is_valid():
            genekey = form.save(commit=False)
            genekey.added_by = user
            genekey.modified_by = user
            genekey.save()
            return redirect('pending_keys', pk=panel.pk)
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
    return render(request, 'main/includes/partial_genes_dropdown_list_options.html', {'genes': genes})


def key_archive(request, pk, key):
    user = request.user
    panel = get_object_or_404(Panel, pk=pk)
    key = get_object_or_404(GeneKey, pk=key)
    data = dict()
    if request.method == 'POST':
        key.archived = True
        key.archived_by = user
        key.archived_at = datetime.now()
        key.modified_by = user
        key.save()
        # This is just to play along with the existing code
        data['form_is_valid'] = True
        active_gene_keys = GeneKey.objects.filter(
            panel=panel.id).exclude(archived=True).exclude(checked=False).order_by('-added_at')
        archived_gene_keys = GeneKey.objects.filter(
            panel=panel.id).exclude(archived=False).exclude(checked=False).order_by('-added_at')
        data['html_key_list_active'] = render_to_string('main/includes/partial_key_list_active.html', {
            'panel': panel,
            'active_gene_keys': active_gene_keys,
            'user': user,
        })
        data['html_key_list_archived'] = render_to_string('main/includes/partial_key_list_archived.html', {
            'panel': panel,
            'archived_gene_keys': archived_gene_keys,
            'user': user
        })
    else:
        context = {
            'panel': panel,
            'key': key,
            'user': user}
        data['html_form'] = render_to_string(
            'main/includes/partial_key_archive.html', context, request=request)
    return JsonResponse(data)


def save_panel_gene_form(request, form, template_name, pk, panel_gene):
    user = request.user
    panel = get_object_or_404(Panel, pk=pk)
    panel_gene = get_object_or_404(PanelGene, id=panel_gene)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            panel_gene = form.save(commit=False)
            panel_gene.modified_by = user
            panel_gene.save()
            data['form_is_valid'] = True
            panel_genes = PanelGene.objects.filter(panel=pk)
            data['html_panel_gene_list'] = render_to_string('main/includes/partial_panel_gene_list.html', {
                'panel': panel,
                'panel_gene': panel_gene,
                'panel_genes': panel_genes,
                'user': user
            })
        else:
            data['form_is_valid'] = False
    context = {'user': user,
               'panel': panel,
               'panel_gene': panel_gene,
               'form': form}
    data['html_form'] = render_to_string(
        template_name, context, request=request)
    return JsonResponse(data)


def panel_gene_edit(request, pk, panel_gene):
    item = get_object_or_404(PanelGene, id=panel_gene)
    if request.method == 'POST':
        form = PanelGeneForm(request.POST, instance=item)
        form.fields['preferred_transcript'].queryset = Transcript.objects.filter(
            Gene=item.gene.id)
    else:
        form = PanelGeneForm(instance=item)
        form.fields['preferred_transcript'].queryset = Transcript.objects.filter(
            Gene=item.gene.id)
    return save_panel_gene_form(request, form, 'main/includes/partial_panel_gene_edit.html', pk, panel_gene)


def save_key_comment_form(request, form, template_name, pk, key):
    user = request.user
    panel = get_object_or_404(Panel, pk=pk)
    key = get_object_or_404(GeneKey, pk=key)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.modified_by = user
            comment.save()
            data['form_is_valid'] = True
            active_gene_keys = GeneKey.objects.filter(
                panel=panel.id).exclude(archived=True).exclude(checked=False).order_by('-added_at')
            data['html_key_list_active'] = render_to_string('main/includes/partial_key_list_active.html', {
                'panel': panel,
                'active_gene_keys': active_gene_keys,
                'key': key,
                'user': user
            })
        else:
            data['form_is_valid'] = False
    context = {'panel': panel,
               'key': key,
               'form': form,
               'user': user}
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
    pending_gene_keys = GeneKey.objects.all().exclude(
        checked=True).order_by('-added_at')

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
        key.modified_by = user
        key.save()
        # This is just to play along with the existing code
        data['form_is_valid'] = True
        pending_gene_keys = GeneKey.objects.all().exclude(
            checked=True).order_by('-added_at')
        data['html_key_list_pending'] = render_to_string('main/includes/partial_key_list_pending.html', {
            'panel': panel,
            'pending_gene_keys': pending_gene_keys,
            'user': user
        })
    else:
        context = {
            'panel': panel,
            'key': key,
            'user': user}
        data['html_form'] = render_to_string(
            'main/includes/partial_key_accept.html', context, request=request)
    return JsonResponse(data)


@login_required
def generate_output(request, pk):
    panel = get_object_or_404(Panel, pk=pk)
    panels = Panel.objects.all()

    context = {
        'title': 'Generate output files',
        'panel': panel,
        'panels': panels
    }

    return render(request, 'main/generate_output.html', context)


def generate_excel(request, pk):
    panel = get_object_or_404(Panel, pk=pk)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{panel}_Gene_Index_{datetime.now().strftime("%Y-%m-%d__%H-%M-%S")}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('diagnostic_request_dictionary')
    ws2 = wb.add_sheet('selected_transcript')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # First Sheet
    columns = ['Key', 'Gene list', 'Panel',
               'Added by', 'Date', 'Checked by', 'Date', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Second Sheet
    columns2 = ['Transcript', 'Gene', ]

    for col_num in range(len(columns2)):
        ws2.write(row_num, col_num, columns2[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    # First Sheet
    active_gene_keys = GeneKey.objects.filter(
        panel=panel).exclude(archived=True).exclude(checked=False).order_by('-added_at')

    for row in active_gene_keys:
        row_num += 1
        ws.write(row_num, 0, row.key, font_style)
        ws.write(row_num, 1, row.gene_names(), font_style)
        ws.write(row_num, 2, row.panel.name, font_style)
        ws.write(row_num, 3, row.added_by.username, font_style)
        ws.write(row_num, 4, row.added_at.strftime('%d/%m/%Y'), font_style)
        ws.write(row_num, 5, row.checked_by.username, font_style)
        ws.write(row_num, 6, row.checked_at.strftime('%d/%m/%Y'), font_style)

    # Second Sheet
    panel_genes = PanelGene.objects.filter(panel=panel)

    row_num = 0
    for row in panel_genes:
        row_num += 1
        ws2.write(row_num, 0, row.preferred_transcript.name, font_style)
        ws2.write(row_num, 1, row.gene.name, font_style)

    # Save excel document
    wb.save(response)
    return response
