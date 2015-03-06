# coding=utf-8
from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

import zendesk

# método da api zendesk faltando na biblioteca (zendesk)
zendesk.mapping_table_v2['list_tickets'] = {
    'path': '/views/{{view_id}}/tickets.json',
    'valid_params': ('view_id',),
    'status': 200,
    'method': 'GET'
}