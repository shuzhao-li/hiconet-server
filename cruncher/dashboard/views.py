import importlib

from django.conf import settings
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from cruncher import celery_app

from .models import ClientRequest, ClientRequestResult


STATE_MESSAGES = {
    'PENDING': 'Your task is awaiting processing.',
    'STARTED': 'Your task is currently processing.',
    'RETRY': 'Your task is awaiting processing (retrying).',
    'SUCCESS': 'Your task has completed - results are available.',
    'FAILURE': 'Your task has failed to process. Please try again.',
    'REVOKED': 'Your task has been cancelled.',
}


def index_view(request):
    engines = settings.CRUNCHER_ENGINES
    if len(engines) == 1:
        return redirect('submit', analysis=engines[0])

    return render(request, 'dashboard/index.html', {'engines': engines})


def submit_view(request, analysis=None):
    try:
        module_path = 'cruncher.{}.forms'.format(analysis)
        forms_mod = importlib.import_module(module_path)
    except ImportError:
        raise Http404('No analysis engine "{}" found'.format(analysis))
    else:
        ClientRequestForm = forms_mod.ClientRequestForm

    if request.method == 'POST':
        form = ClientRequestForm(request.POST, request.FILES)
        if form.is_valid():
            client_request = form.save(commit=False)
            if not client_request.raw_data:
                client_request.data_from_file(request.FILES['datafile'])
            client_request.save()
            task = celery_app.send_task(
                'cruncher.{}.tasks.process_data'.format(analysis),
                args=[client_request.pk])
            client_request.task_id = task.id
            client_request.save()

            return redirect('status', task_id=task.id)
    else:
        initial = {
            'analysis_type': analysis,
        }
        form = ClientRequestForm(initial=initial)

    return render(request, 'dashboard/submit.html', {'form': form})


def status_view(request, task_id=None):
    get_object_or_404(ClientRequest, task_id=task_id)
    result = celery_app.AsyncResult(task_id)
    message = STATE_MESSAGES.get(result.state)

    context = {
        'task_id': task_id,
        'state': result.state,
        'message': message,
        'result_url': reverse_lazy(request, 'result', {'task_id': task_id}),
    }
    return render(request, 'dashboard/status.html', context)


def result_view(request, task_id=None):
    client_request = get_object_or_404(ClientRequest, task_id=task_id)
    result = client_request.results.first()

    context = {
        'task_id': task_id,
        'client_request': client_request,
        'result': result,
    }
    available_templates = [
        '{}/results.html'.format(client_request.analysis_type),
        'dashboard/results.html'
    ]
    return render(request, available_templates, context)
