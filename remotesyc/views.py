from django.http import HttpResponse
import json
import tasks


def sync(request):
    params = {
        'status': True
    }
    try:
        params['sync_total'] = tasks.sync_remote()
    except Exception as e:
        params['status'] = False
        params['error'] = str(e)
    return HttpResponse(json.dumps(params), content_type='application/json')