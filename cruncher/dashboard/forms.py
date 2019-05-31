from django import forms

from .models import ClientRequest


class ClientRequestForm(forms.ModelForm):
    # Allow file upload or copy/paste
    datafile = forms.FileField(required=False)
    raw_data = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = ClientRequest
        fields = [
            'project_name',
            'email',
            'analysis_type',
            'datafile',
            'raw_data',
        ]
        widgets = {
            'analysis_type': forms.HiddenInput()
        }

    def clean(self, validate_raw_data=True):
        cleaned_data = super().clean()
        datafile = cleaned_data.get('datafile')
        raw_data = cleaned_data.get('raw_data')
        if validate_raw_data and not (raw_data or datafile):
            raise forms.ValidationError(
                'Either raw data or a data file is required')
