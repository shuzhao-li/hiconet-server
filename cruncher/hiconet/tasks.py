'''Background worker tasks for HiCoNet analysis'''
import json
import logging
import time

from celery import shared_task
from hiconet.HiCoNet import webHiCoNet
from hiconet.html_visual import make_js_from_network
from cruncher.dashboard.models import ClientRequest, ClientRequestResult

log = logging.getLogger(__name__)


@shared_task
def process_data(request_id):
    log.info('Received HiCoNet processing request [id={}]'.format(request_id))
    request = ClientRequest.objects.get(pk=request_id)
    project = json.loads(request.raw_data)

    # Process data
    log.info(
        'Loading HiCoNet engine for project "{}"'.format(
            project.get('project')))
    engine = webHiCoNet(project)
    log.info('Running HiCoNet processing')
    start = time.time()
    engine.run_hiconet()
    elapsed = time.time() - start
    log.info('HiCoNet processing complete [elapsed={}]'.format(elapsed))

    # Build result
    js_snippet = make_js_from_network(engine.combined_network[:20])
    result = ClientRequestResult(
        request=request,
        processing_seconds=elapsed,
        result_data=js_snippet)
    result.save()

    return result.pk
