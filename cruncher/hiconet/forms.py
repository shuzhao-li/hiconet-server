import json
from django import forms
from cruncher.dashboard.forms import ClientRequestForm as BaseForm
from cruncher.dashboard.models import ClientRequest


class ClientRequestForm(BaseForm):
    #
    # This will be split, so that each data type should have its own Form,
    # and show up as its own box in UI. 
    # Thus more than two data types will be possible and UI can be extended dynamically.
    #
    transcriptomics_name = forms.CharField()
    transcriptomics_data = forms.FileField(
        help_text='Data type 1, data matrix file')
    transcriptomics_feature_annotations = forms.FileField(
        required=False,
        help_text='Data type 1, feature annotation file')
    transcriptomics_observation_annotations = forms.FileField(
        required=False,
        help_text='Data type 1, observation annotation file')


    # terms transcriptomics and metabolomics will be replaced to generic.
    metabolomics_name = forms.CharField()
    metabolomics_data = forms.FileField(
        help_text='Data type 2, data matrix file')
    metabolomics_feature_annotations = forms.FileField(
        required=False,
        help_text='Data type 2, feature annotations file')
    metabolomics_observation_annotations = forms.FileField(
        required=False,
        help_text='Data type 2, observation annotations file')

    class Meta:
        model = ClientRequest
        fields = [
            'project_name',
            
            'analysis_type',
            'transcriptomics_name',
            'transcriptomics_data',
            'transcriptomics_feature_annotations',
            'transcriptomics_observation_annotations',
            
            'metabolomics_name',
            'metabolomics_data',
            'metabolomics_feature_annotations',
            'metabolomics_observation_annotations',

            'email',
        ]
        widgets = {
            'analysis_type': forms.HiddenInput(),
            'raw_data': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('datafile')
        self.fields.pop('raw_data')

    def clean(self):
        # Ignore raw_data checks from parent class
        return super().clean(validate_raw_data=False)

    def _read_csv_data(self, fileobj):
        return fileobj.read().decode(encoding=fileobj.charset or 'utf8')

    def _build_project_definition(self):
        data = self.cleaned_data

        project_dict = {
            'project': data.get('project_name', ''),
            'source_id': 'Cruncher',
            'data_from': data.get('email', ''),
            'societies': [],
        }

        # Transcriptomics
        transcriptomics_features = data.get(
            'transcriptomics_feature_annotations')
        transcriptomics_observations = data.get(
            'transcriptomics_observation_annotations')
        transcriptomics_society = {
            'name': data.get('transcriptomics_name'),
            'datatype': 'transcriptomics',
            'file_data_matrix': self._read_csv_data(
                data.get('transcriptomics_data')),
            'file_feature_annotation': (
                self._read_csv_data(transcriptomics_features)
                if transcriptomics_features else ''),
            'file_observation_annotation': (
                self._read_csv_data(transcriptomics_observations)
                if transcriptomics_observations else ''),
            'file_unstructured': '',
        }
        project_dict['societies'].append(transcriptomics_society)

        # Metabolomics
        metabolomics_features = data.get(
            'metabolomics_feature_annotations')
        metabolomics_observations = data.get(
            'metabolomics_observation_annotations')
        metabolomics_society = {
            'name': data.get('metabolomics_name'),
            'datatype': 'metabolomics',
            'file_data_matrix': self._read_csv_data(
                data.get('metabolomics_data')),
            'file_feature_annotation': (
                self._read_csv_data(metabolomics_features)
                if metabolomics_features else ''),
            'file_observation_annotation': (
                self._read_csv_data(metabolomics_observations)
                if metabolomics_observations else ''),
            'file_unstructured': '',
        }
        project_dict['societies'].append(metabolomics_society)
        return project_dict

    def save(self, commit=True):
        client_request = super().save(commit=False)
        if not client_request.raw_data:
            project_dict = self._build_project_definition()
            client_request.raw_data = json.dumps(project_dict)
        if commit:
            client_request.save()
        return client_request
