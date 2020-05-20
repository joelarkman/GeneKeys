import xlwt
from datetime import datetime
from django.utils import timezone
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
    # Retrieve all Panels.
    panels = Panel.objects.all()

    context = {
        'panels': panels
    }

    # Send panels as context to home page template.
    return render(request, 'main/home.html', context)


def panel_keys(request, pk):
    # Retrieve selected panel.
    panel = get_object_or_404(Panel, pk=pk)
    # Retrieve list of active keys for that panel.
    active_gene_keys = GeneKey.objects.filter(
        panel=pk).exclude(archived=True).exclude(checked=False).order_by('-added_at')
    # Retrieve list of archived keys for that panel.
    archived_gene_keys = GeneKey.objects.filter(
        panel=pk).exclude(archived=False).exclude(checked=False).order_by('-added_at')
    # Retrieve list of genes/preferred transcripts for that panel.
    panel_genes = PanelGene.objects.filter(panel=pk).order_by('gene__name')

    context = {
        'title': panel.name,
        'panel': panel,
        'active_gene_keys': active_gene_keys,
        'archived_gene_keys': archived_gene_keys,
        'panel_genes': panel_genes
    }

    # Send retrieved information as context to panel_keys template.
    return render(request, 'main/panel_keys.html', context)


@login_required  # Page requires authorisation.
def add_key(request, pk):
    # Retreive selected panel.
    panel = get_object_or_404(Panel, pk=pk)
    # Retrieve authorised user.
    user = request.user

    # If form is posted...
    if request.method == 'POST':
        # Load populated form with post information.
        form = AddKeyForm(request.POST)
        # If form populated with valid information...
        if form.is_valid():
            # Initiate form sabing.
            genekey = form.save(commit=False)
            # Override added_by field to authorised user.
            genekey.added_by = user
            # Override modified_by field to authorised user.
            genekey.modified_by = user
            # Finalise form saving.
            genekey.save()
            # Redirect users to pending keys view.
            return redirect('pending_keys', pk=panel.pk)
    else:
        # Initially load form and initialise panel field with selected panel.
        form = AddKeyForm(initial={'panel': pk})

    context = {
        'title': 'Add key',
        'form': form,
        'panel': panel
    }

    # Send form and panel to add_key template.
    return render(request, 'main/add_key.html', context)


@login_required # Page requires authorisation.
def pending_keys(request, pk):
    # Retrieve selected panel.
    panel = get_object_or_404(Panel, pk=pk)
    # Retrieve list of pending keys.
    pending_gene_keys = GeneKey.objects.all().exclude(
        checked=True).order_by('-added_at')

    context = {
        'title': 'Pending Keys',
        'panel': panel,
        'pending_gene_keys': pending_gene_keys
    }

    # Send retrieved information to pending_keys template.
    return render(request, 'main/pending_keys.html', context)


@login_required  # Page requires authorisation.
def generate_output(request, pk):
    # Retrieve selected panel.
    panel = get_object_or_404(Panel, pk=pk)
    # Retrieve all panels.
    panels = Panel.objects.all()

    context = {
        'title': 'Generate output files',
        'panel': panel,
        'panels': panels
    }

    # Send retrieved context to generate_output template.
    return render(request, 'main/generate_output.html', context)


######################
##### AJAX Views #####
######################


def load_genes(request):
    # Retrieve panel field data.
    panel_id = request.GET.get('panel')
    # Retrieve genes associated with panel field.
    genes = Panel.objects.get(pk=panel_id).genes.all().order_by('name')
    # Send list of genes on panel to partial_genes_dropdown_list_options template.
    return render(request, 'main/includes/partial_genes_dropdown_list_options.html', {'genes': genes})


######################
##### CRUD Views #####
######################


def key_archive(request, pk, key):
    # Define a data storage dictionary.
    data = dict()
    # Retrieve authorised user.
    user = request.user
    # Retrieve selected panel.
    panel = get_object_or_404(Panel, pk=pk)
    # Retreive the key attempting to be archived.
    key = get_object_or_404(GeneKey, pk=key)

    # If the key has now been archived by another user, return a relevent error message modal as a JsonResponse.
    if key.archived:
        data['form_is_valid'] = False
        context = {
            'panel': panel}
        data['html_form'] = render_to_string(
            'main/includes/errors/partial_error_cant_archive.html', context)
        return JsonResponse(data)

    # If archive attempt confirmed...
    if request.method == 'POST':
        # Set key to archived.
        key.archived = True
        # Update archived_by, archived_at and modified_by fields.
        key.archived_by = user
        key.archived_at = timezone.now()
        key.modified_by = user
        # Save changes.
        key.save()
        # Set form to valid to inform ajax to close modal and update tables.
        data['form_is_valid'] = True
        # Retrieve updated list of active keys.
        active_gene_keys = GeneKey.objects.filter(
            panel=panel.id).exclude(archived=True).exclude(checked=False).order_by('-added_at')
        # Retrieve updated list of archived keys.
        archived_gene_keys = GeneKey.objects.filter(
            panel=panel.id).exclude(archived=False).exclude(checked=False).order_by('-added_at')
        # Add the updated list html to data to allow tables to be updated.
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
        # Initially add html for a confirmatatory modal to data, with the ability to confirm or cancel archive request.
        context = {
            'panel': panel,
            'key': key,
            'user': user}
        data['html_form'] = render_to_string(
            'main/includes/partial_key_archive.html', context, request=request)
    # Send data as JsonResponse.
    return JsonResponse(data)


def key_comment(request, pk, key):
    # Retrieve the key whose comment is to be accessed.
    instance = get_object_or_404(GeneKey, pk=key)
    # If comment form is submitted...
    if request.method == 'POST':
        # Load comment form with request data.
        form = KeyCommentForm(request.POST, instance=instance)
        # Extract stored time value from hidden form input.
        stored_time = request.POST.get('stored_time')
    else:
        # Initially load comment form, instantiated with the correct key.
        form = KeyCommentForm(instance=instance)
        # Create a blank stored_time variable.
        stored_time = ''
    # Send form, its template, and context information to save view for further processing.
    return save_key_comment_form(request, form, 'main/includes/partial_key_comment.html', pk, key, stored_time)


def save_key_comment_form(request, form, template_name, pk, key, stored_time):
    # Define a data storage dictionary.
    data = dict()
    # Retrieve authorised user.
    user = request.user
    # Retrieve selected panel.
    panel = get_object_or_404(Panel, pk=pk)
    # # Retrieve the key whose comment is to be edited.
    key = get_object_or_404(GeneKey, pk=key)

    # If the key has now been archived by another user, return a relevent error message modal as a JsonResponse.
    if key.archived:
        data['form_is_valid'] = False
        context = {
            'panel': panel}
        data['html_form'] = render_to_string(
            'main/includes/errors/partial_error_cant_comment.html', context)
        return JsonResponse(data)  # Return warning modal.

    # If comment form is submitted...
    if request.method == 'POST':
        # And the provided comment field is valid.
        if form.is_valid():
            # Check if stored_time variable is different to the database modified_at value.
            # This would indicate that another user has updated comment whilst the modal has been open.
            if stored_time != key.modified_at.strftime("%Y-%m-%d__%H-%M-%S.%f"):
                # Update html for comment form modal to contain a 'change' error message.
                # Reload KeyCommentForm instance to display latest version of comment.
                data['form_is_valid'] = False
                context = {'panel': panel,
                           'key': key,
                           'form': KeyCommentForm(instance=key),
                           'user': user,
                           'change': True}
                data['html_form'] = render_to_string(template_name,
                                                     context,
                                                     request=request)
                # Return JsonResponse here to update modal.
                return JsonResponse(data)
            else:
                # If another user has not updated the comment, initialise comment saving.
                comment = form.save(commit=False)
                # Overide modified_by field.
                comment.modified_by = user
                # Finalise saving.
                comment.save()
                # Set form to valid to inform ajax to close modal.
                data['form_is_valid'] = True
    # Initially add html for comment form modal to data, with the ability to view and modify the key's comment.
    context = {'panel': panel,
               'key': key,
               'form': form,
               'user': user}
    data['html_form'] = render_to_string(
        template_name, context, request=request)
    # Send data as JsonResponse.
    return JsonResponse(data)


def panel_gene_edit(request, pk, panel_gene):
    # Retrieve the PanelGene whose preferred transcript is to be modifed.
    instance = get_object_or_404(PanelGene, id=panel_gene)
    # Set q_set to be list of transcripts that exist for the relevent gene.
    q_set = Transcript.objects.filter(
        Gene=instance.gene.id)
    # If preferred transcript form is submitted...
    if request.method == 'POST':
        # Load PanelGeneForm with request data.
        form = PanelGeneForm(request.POST, instance=instance)
        # Extract stored time value from hidden form input.
        stored_time = request.POST.get('stored_time')
    else:
        # Initially, load PanelGeneForm instantiated with the correct PanelGene.
        form = PanelGeneForm(instance=instance)
        # Update the preferref_trancript field dropdown to display q_set.
        form.fields['preferred_transcript'].queryset = q_set
        # Create a blank stored_time variable.
        stored_time = ''
    # Send form, its template, and context information to save view for further processing.
    return save_panel_gene_form(request, form, 'main/includes/partial_panel_gene_edit.html', pk, panel_gene, q_set, stored_time)


def save_panel_gene_form(request, form, template_name, pk, panel_gene, q_set, stored_time):
    # Define a data storage dictionary.
    data = dict()
    # Retrieve authorised user.
    user = request.user
    # Retrieve selected panel.
    panel = get_object_or_404(Panel, pk=pk)
    # Retrieve the panel_gene whose preferred transcipt is to be modified.
    panel_gene = get_object_or_404(PanelGene, id=panel_gene)

    # If PanelGeneForm is submitted..
    if request.method == 'POST':
        # And if the provided input is valid.
        if form.is_valid():
            # Check if stored_time variable is different to the database modified_at value.
            # This would indicate that another user has updated comment whilst the modal has been open.
            if stored_time != panel_gene.modified_at.strftime("%Y-%m-%d__%H-%M-%S.%f"):
                # Update html for PanelGeneForm modal to contain a 'change' error message.
                # Reload PanelGeneForm instance to display latest preferred transcript.
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
                # Return JsonResponse here to update modal.
                return JsonResponse(data)
            else:
                # If another user has not updated the entry, initialise form saving.
                panel_gene = form.save(commit=False)
                # Overide the modified_by field to the authorised user.
                panel_gene.modified_by = user
                # Finalise saving.
                panel_gene.save()
                # Set form to valid to inform ajax to close modal and update table.
                data['form_is_valid'] = True
                # Retrieve updated list of genes/preferred transcripts.
                panel_genes = PanelGene.objects.filter(
                    panel=pk).order_by('gene__name')
                # Add the updated list html to data to allow tables to be updated.
                data['html_panel_gene_list'] = render_to_string('main/includes/partial_panel_gene_list.html', {
                    'panel': panel,
                    'panel_gene': panel_gene,
                    'panel_genes': panel_genes,
                    'user': user
                })
    # Initially add html for PanelGeneForm modal to data, with the ability to view and modify the preferred transctipt.
    context = {'user': user,
               'panel': panel,
               'panel_gene': panel_gene,
               'form': form,
               'q_set': q_set}
    data['html_form'] = render_to_string(
        template_name, context, request=request)
    # Send data as JsonResponse.
    return JsonResponse(data)


def key_accept(request, pk, key):
    # Define a data storage dictionary.
    data = dict()
    # Retrieve authorised user.
    user = request.user
    # Retrieve selected panel.
    panel = get_object_or_404(Panel, pk=pk)

    # Try and retrieve the key to be accepted.
    try:
        key = get_object_or_404(GeneKey, pk=key)

    # If this fails, assume the key had been deleted by another user.
    except:
        # Return relevent error message as JsonResponse.
        data['form_is_valid'] = False
        context = {
            'panel': panel}
        data['html_form'] = render_to_string(
            'main/includes/errors/partial_error_cant_accept_deleted.html', context)
        return JsonResponse(data)

    # If retrieved key has now been checked by another user, return a relevent error message modal as a JsonResponse.
    if key.checked:
        data['form_is_valid'] = False
        context = {
            'panel': panel}
        data['html_form'] = render_to_string(
            'main/includes/errors/partial_error_cant_accept_accepted.html', context)
        return JsonResponse(data)

    # If confirmatory modal is conirmed...
    if request.method == 'POST':
        # Set key to checked
        key.checked = True
        # Update checked_by, checked_at and modified_by fields.
        key.checked_by = user
        key.checked_at = timezone.now()
        key.modified_by = user
        # Save changes.
        key.save()
        # Set form to valid to inform ajax to close modal and update tables.
        data['form_is_valid'] = True
        # Retrieve updated list of pending keys.
        pending_gene_keys = GeneKey.objects.all().exclude(
            checked=True).order_by('-added_at')
        # Add the updated list html to data to allow tables to be updated.
        data['html_key_list_pending'] = render_to_string('main/includes/partial_key_list_pending.html', {
            'panel': panel,
            'pending_gene_keys': pending_gene_keys,
            'user': user
        })
    else:
        # Initially add html for a confirmatatory modal to data, with the ability to confirm or cancel accept request.
        context = {
            'panel': panel,
            'key': key,
            'user': user}
        data['html_form'] = render_to_string(
            'main/includes/partial_key_accept.html', context, request=request)
    # Send data as JsonResponse.
    return JsonResponse(data)


def key_delete(request, pk, key):
    # Define a data storage dictionary.
    data = dict()
    # Retrieve authorised user.
    user = request.user
    # Retrieve selected panel.
    panel = get_object_or_404(Panel, pk=pk)

    # Try and retrieve the key to be deleted.
    try:
        key = get_object_or_404(GeneKey, pk=key)

    # If this fails, assume the key had already been deleted by another user.
    except:
        # Return relevent error message as JsonResponse.
        data['form_is_valid'] = False
        context = {
            'panel': panel}
        data['html_form'] = render_to_string(
            'main/includes/errors/partial_error_cant_delete_deleted.html', context)
        return JsonResponse(data)

    # If retrieved key has instead been checked by another user, return a relevent error message modal as a JsonResponse.
    if key.checked:
        data['form_is_valid'] = False
        context = {
            'panel': panel}
        data['html_form'] = render_to_string(
            'main/includes/errors/partial_error_cant_delete_accepted.html', context)
        return JsonResponse(data)

    # If confirmatory modal is conirmed...
    if request.method == 'POST':
        # Delete key
        key.delete()
        # Set form to valid to inform ajax to close modal and update tables.
        data['form_is_valid'] = True
        # Retrieve updated list of pending keys.
        pending_gene_keys = GeneKey.objects.all().exclude(
            checked=True).order_by('-added_at')
        # Add the updated list html to data to allow tables to be updated.
        data['html_key_list_pending'] = render_to_string('main/includes/partial_key_list_pending.html', {
            'panel': panel,
            'pending_gene_keys': pending_gene_keys,
            'user': user
        })
    else:
        # Initially add html for a confirmatatory modal to data, with the ability to confirm or cancel accept request.
        context = {
            'panel': panel,
            'key': key,
            'user': user}
        data['html_form'] = render_to_string(
            'main/includes/partial_key_delete.html', context, request=request)
    # Send data as JsonResponse.
    return JsonResponse(data)


#############################
##### Output Generation #####
#############################


def generate_excel(request, pk):
    # Retrieve selected panel.
    panel = get_object_or_404(Panel, pk=pk)
    # Initiate a Http response of the type MS excel.
    response = HttpResponse(content_type='application/ms-excel')
    # Define filename structure of excel document (To include timstamp and name of selected panel).
    response['Content-Disposition'] = f'attachment; filename="{panel}_Gene_Index_{datetime.now().strftime("%Y-%m-%d__%H-%M-%S")}.xls"'

    # Create an excel workbook.
    wb = xlwt.Workbook(encoding='utf-8')

    # Add 'diagnostic_request_dictionary' sheet.
    ws = wb.add_sheet('diagnostic_request_dictionary')
    # Protect the sheet with a difficult password.
    ws.protect = True
    ws.password = 'hEdraf-qunzer-gidbo1'
    # Freeze top row.
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(1)

    # Add 'selected_transcripts' sheet.
    ws2 = wb.add_sheet('selected_transcripts')
    # Protect the sheet with a difficult password.
    ws2.protect = True
    ws2.password = 'hEdraf-qunzer-gidbo1'
    # Freeze top row.
    ws2.set_panes_frozen(True)
    ws2.set_horz_split_pos(1)

    # Set to first row.
    row_num = 0

    # First sheet header

    # Define default font style.
    font_style = xlwt.XFStyle()

    # Turn on bold text.
    font_style.font.bold = True

    # Specify column names of first sheet.
    columns = ['Key', 'Gene list', 'Panel',
               'Added by', 'Date', 'Checked by', 'Date', ]

    # Modify width of first column.
    ws.col(1).width = int(80*260)

    # Print column names in first row.
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Second Sheet header.

    # Specify column names of second sheet.
    columns2 = ['Transcript', 'Gene', ]

    # Modify width of first two columns.
    ws2.col(0).width = int(15*260)
    ws2.col(1).width = int(15*260)

    # Print column names in first row.
    for col_num in range(len(columns2)):
        ws2.write(row_num, col_num, columns2[col_num], font_style)

    # Turn of bold text for body of both sheets.
    font_style = xlwt.XFStyle()

    # First Sheet body

    # Retrieve active keys for the selected panel
    active_gene_keys = GeneKey.objects.filter(
        panel=panel).exclude(archived=True).exclude(checked=False).order_by('-added_at')

    # For each active key, print the relevent data to each column.
    for row in active_gene_keys:
        row_num += 1
        ws.write(row_num, 0, row.key, font_style)
        ws.write(row_num, 1, row.gene_names(), font_style)
        ws.write(row_num, 2, row.panel.name, font_style)
        ws.write(row_num, 3, row.added_by.username, font_style)
        ws.write(row_num, 4, row.added_at.strftime('%d/%m/%Y'), font_style)
        ws.write(row_num, 5, row.checked_by.username, font_style)
        ws.write(row_num, 6, row.checked_at.strftime('%d/%m/%Y'), font_style)

    # Second Sheet body

    # Reteive gene/preferred transcript list.
    panel_genes = PanelGene.objects.filter(panel=panel).order_by('gene__name')

    row_num = 0  # Reset to row 0.
    # For each gene/transcript, print the relevent data to each column.
    for row in panel_genes:
        row_num += 1
        # Only try to print into transcript column if a preferred transcript exists.
        if row.preferred_transcript:
            ws2.write(row_num, 0, row.preferred_transcript.name, font_style)
        ws2.write(row_num, 1, row.gene.name, font_style)

    # Save excel document
    wb.save(response)

    # Send to document back to output page as a response.
    return response


###############
##### API #####
###############


class PanelAPIView(generics.ListAPIView):
    # Use panel serializer.
    serializer_class = PanelSerializer

    def get_queryset(self):
        # Set queryset to blank initially.
        queryset = Panel.objects.none()
        # Check is user has made a panel query.
        panel = self.request.query_params.get('panel', None)
        # If they have...
        if panel is not None:
            try:
                # try converying it to a number and using that to extract a panel.
                panel = float(panel)
                queryset = Panel.objects.filter(id=panel)
            except ValueError:
                # if that doesnt work use it as a string and search for panels containing that string.
                queryset = Panel.objects.filter(name__contains=panel.upper())
        # Return resultant queryset.
        return queryset


class GeneKeyAPIView(generics.ListAPIView):
    # Use GeneKey serializer.
    serializer_class = GeneKeySerializer

    def get_queryset(self):
        # Set queryset to blank initially.
        queryset = GeneKey.objects.none()
        # Extract panel from key word arguments.
        panel = self.kwargs['panel']
        try:
            # try converying it to a number and using that to extract a panel.
            panel = float(panel)
            queryset = GeneKey.objects.filter(panel=panel).exclude(
                archived=True).exclude(checked=False).order_by('-added_at')
        except ValueError:
            # if that doesnt work use it as a string and search for a panel containing that string.
            queryset = GeneKey.objects.filter(panel__name=panel.upper()).exclude(
                archived=True).exclude(checked=False).order_by('-added_at')
        # Return resultant queryset.
        return queryset


class PanelGeneAPIView(generics.ListAPIView):
    # Use PanelGene serializer.
    serializer_class = PanelGeneSerializer

    def get_queryset(self):
        # Set queryset to blank initially.
        queryset = PanelGene.objects.none()
        # Extract panel from key word arguments.
        panel = self.kwargs['panel']
        try:
            # try converying it to a number and using that to extract a panel.
            panel = float(panel)
            queryset = PanelGene.objects.filter(
                panel=panel).order_by('gene__name')
        except ValueError:
            # if that doesnt work use it as a string and search for a panel containing that string.
            queryset = PanelGene.objects.filter(
                panel__name=panel.upper()).order_by('gene__name')
        # Return resultant queryset.
        return queryset
