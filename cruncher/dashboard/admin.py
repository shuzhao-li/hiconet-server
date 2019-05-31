from django.contrib import admin
from .models import ClientRequest, ClientRequestResult


class ClientRequestResultsInline(admin.StackedInline):
    model = ClientRequestResult
    extra = 0
    readonly_fields = (
        'processing_seconds', 'result_data', 'created', 'modified',)


class ClientRequestAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified')
    list_display = (
        'project_name', 'email', 'analysis_type', 'created', 'modified')
    list_filter = ('analysis_type',)
    search_fields = ('project_name', 'email')
    inlines = [ClientRequestResultsInline]

    class Meta:
        model = ClientRequest


admin.site.register(ClientRequest, ClientRequestAdmin)
