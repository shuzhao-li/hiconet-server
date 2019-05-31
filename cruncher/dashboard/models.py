import io
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    '''Base model providing creation and modification timestamps'''
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)

#
# This is extended in forms.py
#
class ClientRequest(TimestampedModel):
    '''User request for data processing, identified by email address'''
    project_name = models.CharField(
        max_length=255,
        help_text='Every project needs a good name')

    email = models.EmailField(help_text='Valid email address is useful')

    analysis_type = models.CharField(
        max_length=64, help_text='Type of analysis to be performed')
    raw_data = models.TextField(
        help_text='Raw data for analysis')

    task_id = models.CharField(
        max_length=255, blank=True,
        help_text='Internal unique id for the analysis task')

    def data_from_uploadfile(self, uploadfile):
        self.raw_data = uploadfile.read()

    def __str__(self):
        return '{}: {}'.format(self.project_name, self.analysis_type)


class ClientRequestResult(TimestampedModel):
    '''Model to store result data from data processing for later display'''
    request = models.ForeignKey(
        ClientRequest, on_delete=models.CASCADE, related_name='results')
    processing_seconds = models.FloatField(null=True)
    result_data = models.TextField(blank=True)
