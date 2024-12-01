from __future__ import absolute_import, unicode_literals

import os

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
if os.environ.get('NO_TASKS', False):
    print(f"WARNING: No tasks mode! System ENV: NO_TASKS=1 WARNING")
else:
    from .octo_celery import app as celery_app

    __all__ = ['celery_app']
