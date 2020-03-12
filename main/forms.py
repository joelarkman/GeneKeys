from django import forms
from django.db.models.query import QuerySet

from .models import Gene, GeneKey, Panel


class AddKeyForm(forms.ModelForm):
    class Meta:
        model = GeneKey
        fields = ['panel', 'gene_key', 'genes']

    panel = forms.ModelChoiceField(
        queryset=Panel.objects.all(), empty_label='Choose a panel')

    genes = forms.ModelMultipleChoiceField(queryset=Gene.objects.all())

    # Gene.objects.none(
    # Gene.objects.all()
    # Panel.objects.get(pk=panel).genes.all()

    # Overriding __init__ here allows us to provide initial
    # data for 'toppings' field
    def __init__(self, *args, **kwargs):

        if kwargs.get('instance'):
            # We get the 'initial' keyword argument or initialize it
            # as a dict if it didn't exist.
            initial = kwargs.setdefault('initial', {})
            # The widget for a ModelMultipleChoiceField expects
            # a list of primary key for the selected data.
            initial['genes'] = [t.pk for t in kwargs['instance'].genes.all()]

        forms.ModelForm.__init__(self, *args, **kwargs)

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
