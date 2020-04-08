from django import forms
from django.db.models.query import QuerySet

from .models import Gene, GeneKey, Panel, PanelGene


class AddKeyForm(forms.ModelForm):
    class Meta:
        model = GeneKey

        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'cols': 20}),
        }

        fields = ['panel', 'key', 'genes', 'comment']

    panel = forms.ModelChoiceField(
        queryset=Panel.objects.all(), empty_label='Choose a panel')

    genes = forms.ModelMultipleChoiceField(queryset=Gene.objects.all())

    def __init__(self, *args, **kwargs):

        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['genes'] = [
                gene.pk for gene in kwargs['instance'].genes.all()]

        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['genes'].queryset = Gene.objects.none()

        if 'panel' in self.data:
            try:
                panel_id = int(self.data.get('panel'))
                self.fields['genes'].queryset = Panel.objects.get(
                    pk=panel_id).genes.all()
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty queryset

    # Overriding save allows us to process the value of 'genes' field
    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)

        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            instance.genes.clear()
            instance.genes.add(*self.cleaned_data['genes'])
        self.save_m2m = save_m2m

        instance.save()
        self.save_m2m()

        return instance


class PanelGeneForm(forms.ModelForm):
    class Meta:
        model = PanelGene
        fields = ('preferred_transcript',)
        # fields = ('panel', 'gene', 'transcript')


class KeyCommentForm(forms.ModelForm):
    class Meta:
        model = GeneKey

        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'cols': 20}),
        }

        fields = ('comment',)
