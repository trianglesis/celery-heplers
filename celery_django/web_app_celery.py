"""
Separate Celery settings file

"""

from __future__ import absolute_import, unicode_literals
import os
import django

from celery import Celery
from kombu import Exchange

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_app.settings')
# Setup django project
django.setup()
# curr_hostname = getattr(settings, 'CURR_HOSTNAME', None)
#  The backend is specified via the backend argument to Celery, (or via the result_backend setting if you choose to use a configuration module):
app = Celery('web_app',
             broker='amqp://mq_user:mq_password@localhost:5672/mq_vhost',
             backend='amqp://mq_user:mq_password@localhost:5672/mq_vhost',
             )

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')
#  The backend is specified via the backend argument to Celery, (or via the result_backend setting if you choose to use a configuration module):

if not os.name == "nt":
    # https://github.com/celery/celery/issues/4184
    app.conf.timezone   = 'UTC'
    app.conf.enable_utc   = True

    # Load task modules from all registered Django app configs.
    app.autodiscover_tasks()

    # One for internal:
    default_exchange = Exchange('default',   type = 'direct')
    # One for tests only
    tests_exchange   = Exchange('tests_run', type = 'direct')

    app.conf.update(
        accept_content    = ['json', 'pickle', 'application/x-python', 'application/json', 'application/x-python-serialize'],
        task_serializer   = 'pickle',
        result_serializer = 'json',
        # Do not set! Or logic will not wait of task OK: # task_ignore_result=True,
        # http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#django-celery-results-using-the-django-orm-cache-as-a-result-backend
        result_backend = 'db+mysql://celery_backend:celery_backend_passwd@localhost/web_app_database',


        # result_backend = 'django-db',  # Use if 'django_celery_results'
        # INFO: This added as arg to celery service in Centos init.d | BUT should be used here?
        beat_scheduler             = 'django_celery_beat.schedulers:DatabaseScheduler',
        task_default_queue         = 'default',
        task_default_exchange      = 'default',
        task_default_routing_key   = 'default',
        task_default_exchange_type = 'direct',
        task_create_missing_queues = True,

        # http://docs.celeryproject.org/en/master/userguide/configuration.html#std:setting-worker_prefetch_multiplier
        worker_prefetch_multiplier = 0,
        # worker_prefetch_multiplier = 2000,

        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-worker_send_task_events
        worker_send_task_events = True,
        task_send_sent_event    = True,
        worker_pool_restarts    = True,

        # Maybe this should be disabled to allow workers to get ALL tasks in queue.
        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_acks_late
        # http://docs.celeryproject.org/en/master/faq.html#faq-acks-late-vs-retry
        # task_acks_late = False,

        # Experimental:
        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_persistent
        # result_persistent = True,
        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_track_started
        task_track_started = True,

        # Can produce web errors: [Errno 104] Connection reset by peer???
        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_pool_limit
        # https://stackoverflow.com/questions/45803728/celery-upgrade-3-1-4-1-connection-reset-by-peer
        broker_pool_limit = None,  # Keep connection always up!
        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#broker-connection-timeout
        # broker_connection_timeout     = 2,
        # broker_connection_retry       = True,
        # broker_connection_max_retries = 0,
        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_transport_options
    )

    app.control.add_consumer(
        queue='perforce',
        exchange = 'tests_run',
        exchange_type = 'direct',
        routing_key   = 'perforce.*',
        destination = ['w_perforce@mq_vhost'])

    # Keep parsing with default queue for local and system tasks only:
    app.control.add_consumer(
        queue='parsing',
        exchange = 'tests_run',
        exchange_type = 'direct',
        routing_key   = 'parsing.*',
        destination = ['w_parsing@mq_vhost'])

    app.control.add_consumer(
        queue='routines',
        exchange = 'tests_run',
        exchange_type = 'direct',
        routing_key   = 'routines.*',
        destination = ['w_routines@mq_vhost'])

    # New:
    app.control.add_consumer(
        queue='alpha',
        exchange = 'tests_run',
        exchange_type = 'direct',
        routing_key   = 'alpha.*',
        destination = ['alpha@mq_vhost'])

    app.control.add_consumer(
        queue='beta',
        exchange = 'tests_run',
        exchange_type = 'direct',
        routing_key   = 'beta.*',
        destination = ['beta@mq_vhost'])

    app.control.add_consumer(
        queue='charlie',
        exchange = 'tests_run',
        exchange_type = 'direct',
        routing_key   = 'charlie.*',
        destination = ['charlie@mq_vhost'])

    app.control.add_consumer(
        queue='delta',
        exchange = 'tests_run',
        exchange_type = 'direct',
        routing_key   = 'delta.*',
        destination = ['delta@mq_vhost'])

    app.control.add_consumer(
        queue='echo',
        exchange = 'tests_run',
        exchange_type = 'direct',
        routing_key   = 'echo.*',
        destination = ['echo@mq_vhost'])

    app.control.add_consumer(
        queue='foxtrot',
        exchange = 'tests_run',
        exchange_type = 'direct',
        routing_key   = 'foxtrot.*',
        destination = ['foxtrot@mq_vhost'])

    # AGAIN! I SAID ADD CONSUMER!
    app.control.add_consumer(
        queue='development',
        exchange = 'tests_run',
        exchange_type = 'direct',
        routing_key   = 'development.*',
        destination = ['development@mq_vhost'])

    app.control.cancel_consumer(
        'default',
        destination = [
            'w_perforce@mq_vhost',
            'w_routines@mq_vhost',
            'alpha@mq_vhost',
            'beta@mq_vhost',
            'charlie@mq_vhost',
            'delta@mq_vhost',
            'echo@mq_vhost',
            'foxtrot@mq_vhost',
            'development@mq_vhost',
        ])

# To activate all queues and tasks are left:
# Or better use proper restart/reloas.
# app.control.inspect()
# app.control.inspect().active_queues()
