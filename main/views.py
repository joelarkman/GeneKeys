import xlwt
from datetime import datetime
from rest_framework import generics
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.template.loader import render_to_string

from .forms import AddKeyForm, KeyCommentForm, PanelGeneForm
from .models import Gene, GeneKey, Panel, PanelGene, Transcript
from .serializers import PanelSerializer, GeneKeySerializer, PanelGeneSerializer


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
    panel_genes = PanelGene.objects.filter(panel=pk).order_by('gene__name')

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


######################
##### AJAX Views #####
######################


def load_genes(request):
    panel_id = request.GET.get('panel')
    genes = Panel.objects.get(pk=panel_id).genes.all().order_by('name')
    return render(request, 'main/includes/partial_genes_dropdown_list_options.html', {'genes': genes})


######################
##### CRUD Views #####
######################


def key_archive(request, pk, key):
    user = request.user
    panel = get_object_or_404(Panel, pk=pk)
    key = get_object_or_404(GeneKey, pk=key)
    data = dict()
    if request.method == 'POST':
        if not key.archived:
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


def save_panel_gene_form(request, form, template_name, pk, panel_gene, q_set, stored_time):
    user = request.user
    panel = get_object_or_404(Panel, pk=pk)
    panel_gene = get_object_or_404(PanelGene, id=panel_gene)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            if stored_time != panel_gene.modified_at.strftime("%Y-%m-%d__%H-%M-%S.%f"):
                data['form_is_valid'] = False
                context = {'user': user,
                           'panel': panel,
                           'panel_gene': panel_gene,
                           'form': PanelGeneForm(instance=panel_gene),
                           'q_set': q_set,
                           'change': True}
                data['html_form'] = render_to_string(template_name,
                                                     context,
                                                     request=request)
                return JsonResponse(data)
            else:
                panel_gene = form.save(commit=False)
                panel_gene.modified_by = user
                panel_gene.save()
                data['form_is_valid'] = True
                panel_genes = PanelGene.objects.filter(
                    panel=pk).order_by('gene__name')
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
               'form': form,
               'q_set': q_set}
    data['html_form'] = render_to_string(
        template_name, context, request=request)
    return JsonResponse(data)


def panel_gene_edit(request, pk, panel_gene):
    item = get_object_or_404(PanelGene, id=panel_gene)
    q_set = Transcript.objects.filter(
        Gene=item.gene.id)
    if request.method == 'POST':
        form = PanelGeneForm(request.POST, instance=item)
        form.fields['preferred_transcript'].queryset = q_set
        stored_time = request.POST.get('stored_time')
    else:
        form = PanelGeneForm(instance=item)
        form.fields['preferred_transcript'].queryset = Transcript.objects.filter(
            Gene=item.gene.id)
        stored_time = ''
    return save_panel_gene_form(request, form, 'main/includes/partial_panel_gene_edit.html', pk, panel_gene, q_set, stored_time)


def save_key_comment_form(request, form, template_name, pk, key, stored_time):
    data = dict()
    user = request.user
    panel = get_object_or_404(Panel, pk=pk)
    key = get_object_or_404(GeneKey, pk=key)

    # Check if key is now archived.
    if key.archived:
        context = {
            'panel': panel}
        data['html_form'] = render_to_string(
            'main/includes/partial_key_is_archived.html', context)
        return JsonResponse(data)  # Return warning modal.

    if request.method == 'POST':
        if form.is_valid():
            # Check if stored last modified time is different to the database value.
            if stored_time != key.modified_at.strftime("%Y-%m-%d__%H-%M-%S.%f"):
                # If its been modified but not archived.
                data['form_is_valid'] = False
                context = {'panel': panel,
                            'key': key,
                            'form': KeyCommentForm(instance=key),
                            'user': user,
                            'change': True}
                data['html_form'] = render_to_string(template_name,
                                                        context,
                                                        request=request)
                # Refresh comment modal with 'change' error.
                return JsonResponse(data)
            else:
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
        # Extract stored time value from hidden form input.
        stored_time = request.POST.get('stored_time')
    else:
        form = KeyCommentForm(instance=instance)
        stored_time = ''
    return save_key_comment_form(request, form, 'main/includes/partial_key_comment.html', pk, key, stored_time)


def key_accept(request, pk, key):
    data = dict()
    user = request.user
    panel = get_object_or_404(Panel, pk=pk)
    try:
        key = get_object_or_404(GeneKey, pk=key)
    except:
        context = {
            'panel': panel}
        data['html_form'] = render_to_string(
            'main/includes/partial_key_doesnt_exist.html', context)
        return JsonResponse(data)

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


def key_delete(request, pk, key):
    data = dict()
    user = request.user
    panel = get_object_or_404(Panel, pk=pk)
    key = get_object_or_404(GeneKey, pk=key)
    if key.checked:
        data['form_is_valid'] = False
        context = {
            'panel': panel}
        data['html_form'] = render_to_string(
            'main/includes/partial_key_is_accepted.html', context)
        return JsonResponse(data)

    if request.method == 'POST':
        key.delete()
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
            'main/includes/partial_key_delete.html', context, request=request)
    return JsonResponse(data)


#############################
##### Output Generation #####
#############################


def generate_excel(request, pk):
    panel = get_object_or_404(Panel, pk=pk)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{panel}_Gene_Index_{datetime.now().strftime("%Y-%m-%d__%H-%M-%S")}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')

    ws = wb.add_sheet('diagnostic_request_dictionary')
    ws.protect = True
    ws.password = 'hEdraf-qunzer-gidbo1'
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(1)

    ws2 = wb.add_sheet('selected_transcript')
    ws2.protect = True
    ws2.password = 'hEdraf-qunzer-gidbo1'
    ws2.set_panes_frozen(True)
    ws2.set_horz_split_pos(1)

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # First Sheet
    columns = ['Key', 'Gene list', 'Panel',
               'Added by', 'Date', 'Checked by', 'Date', ]

    ws.col(1).width = int(80*260)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Second Sheet
    columns2 = ['Transcript', 'Gene', ]

    ws2.col(0).width = int(15*260)
    ws2.col(1).width = int(15*260)

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
    panel_genes = PanelGene.objects.filter(panel=panel).order_by('gene__name')

    row_num = 0
    for row in panel_genes:
        row_num += 1

        if row.preferred_transcript:
            ws2.write(row_num, 0, row.preferred_transcript.name, font_style)
        ws2.write(row_num, 1, row.gene.name, font_style)

    # Save excel document
    wb.save(response)
    return response


###############
##### API #####
###############


class PanelAPIView(generics.ListAPIView):
    serializer_class = PanelSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Panel.objects.none()
        panel = self.request.query_params.get('panel', None)
        if panel is not None:
            try:
                panel = float(panel)
                queryset = Panel.objects.filter(id=panel)
            except ValueError:
                queryset = Panel.objects.filter(name__contains=panel.upper())
        return queryset


class GeneKeyAPIView(generics.ListAPIView):
    serializer_class = GeneKeySerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = GeneKey.objects.none()
        panel = self.kwargs['panel']
        try:
            panel = float(panel)
            queryset = GeneKey.objects.filter(panel=panel).exclude(
                archived=True).exclude(checked=False).order_by('-added_at')
        except ValueError:
            queryset = GeneKey.objects.filter(panel__name=panel.upper()).exclude(
                archived=True).exclude(checked=False).order_by('-added_at')
        return queryset


class PanelGeneAPIView(generics.ListAPIView):
    serializer_class = PanelGeneSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = PanelGene.objects.none()
        panel = self.kwargs['panel']
        try:
            panel = float(panel)
            queryset = PanelGene.objects.filter(
                panel=panel).order_by('gene__name')
        except ValueError:
            queryset = PanelGene.objects.filter(
                panel__name=panel.upper()).order_by('gene__name')
        return queryset
