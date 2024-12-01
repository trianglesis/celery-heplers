from __future__ import absolute_import, unicode_literals

import os
import socket

import django
from celery import Celery
from kombu import Exchange

from core.credentials import CeleryCreds, HostnamesSupported, RabbitMQCreds, MySQLDatabase

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

hostname = socket.gethostname()

# 0 is DEV
# 1 is PROD_2
# 2 is PROD_1
ENV = 0
app = None
workers = []
backend = []
result_backend = []
DB_NAME = None


def setup_celery_env():
    global workers
    global backend
    global result_backend
    global DB_NAME
    # LOCAL DEV
    if hostname == HostnamesSupported.LOCAL_DEV_HOST:
        ENV = 0
        DB_NAME = MySQLDatabase.DB_NAME_PROD_2  # Use PROD_2
        workers = CeleryCreds.WSL_WORKERS
        print(f"<== Core Celery ==> LOCAL DEV ENV: {hostname} ENV={ENV}; DB_NAME: {DB_NAME}")
    # PROD_2
    elif hostname == HostnamesSupported.PROD_2:
        ENV = 1
        DB_NAME = MySQLDatabase.DB_NAME_PROD_2  # Use PROD_2
        workers = CeleryCreds.PROD_2_WORKERS
        print(f"<== Core Celery ==> PROD_2 DEV ENV: {hostname} ENV={ENV}; DB_NAME: {DB_NAME}")
    # PROD_1
    else:
        ENV = 2
        DB_NAME = MySQLDatabase.DB_NAME_PROD_1  # Use PROD_1
        workers = CeleryCreds.PROD_1_WORKERS
        print(f"<== Core Celery ==> PROD_1: {hostname} ENV={ENV}; DB_NAME: {DB_NAME}")

    # WSL Options only
    if ENV == 0:
        backend = CeleryCreds.BACKEND.format(
            DB_USER=CeleryCreds.DB_USER,
            DB_PASSWORD=CeleryCreds.DB_PASSWORD,
            DB_HOST=CeleryCreds.DB_HOST_WSL,
            DB_NAME=DB_NAME,
        )
        result_backend = CeleryCreds.RESULT_BACKEND.format(
            DB_USER=CeleryCreds.DB_USER,
            DB_PASSWORD=CeleryCreds.DB_PASSWORD,
            DB_HOST=CeleryCreds.DB_HOST_WSL,
            DB_NAME=DB_NAME,
        )
        print(f"<== Core Celery ==> WSL: {CeleryCreds.DB_HOST_WSL}")
        print(f"<== Core Celery ==> WSL backend: {backend}")
        print(f"<== Core Celery ==> WSL result_backend: {result_backend}")
    else:
        backend = CeleryCreds.BACKEND.format(
            DB_USER=CeleryCreds.DB_USER,
            DB_PASSWORD=CeleryCreds.DB_PASSWORD,
            DB_HOST=CeleryCreds.DB_HOST,
            DB_NAME=DB_NAME,
        )
        result_backend = CeleryCreds.RESULT_BACKEND.format(
            DB_USER=CeleryCreds.DB_USER,
            DB_PASSWORD=CeleryCreds.DB_PASSWORD,
            DB_HOST=CeleryCreds.DB_HOST,
            DB_NAME=DB_NAME,
        )


def skip_celery():
    if os.environ.get('NO_TASKS', False):
        print(f"!!! NO CELERY !!! - Do not initialize Celery APP now, sys ENV used: NO_TASKS = {os.environ.get('NO_TASKS', False)}")
        return True
    return False


def startup_celery():
    if not skip_celery():
        print("\n\n\n")
        print("<== Core Celery ==> Initialize...")
        # Continue
        celery_setup()
    else:
        # Dummy
        global app
        app = Celery()


def celery_setup():
    # Get creds and hosts
    setup_celery_env()
    print(f"Celery set up:"
          f"\n\tworkers: {workers}"
          f"\n\tbackend: {backend}"
          f"\n\tresult_backend: {result_backend}"
          f"\n\tDB_NAME: {DB_NAME}")

    # Setup django project
    django.setup()
    #  The backend is specified via the backend argument to Celery
    global app
    app = Celery('Core',
                 # http://docs.celeryproject.org/en/latest/userguide/optimizing.html
                 broker=RabbitMQCreds.BROKER,
                 # http://docs.celeryproject.org/en/latest/userguide/configuration.html#result-backend
                 backend=backend,
                 )

    # Using a string here means the worker doesn't have to serialize
    # the configuration object to child processes.
    # - namespace='CELERY' means all celery-related configuration keys
    #   should have a `CELERY_` prefix.
    # app.config_from_object('django.conf:settings', namespace='CELERY')
    #  The backend is specified via the backend argument to Celery,
    #  (or via the result_backend setting if you choose to use a configuration module):
    # https://docs.celeryproject.org/en/master/userguide/configuration.html
    app.conf.timezone = 'UTC'
    app.conf.enable_utc = True

    # now use the same for PROD_1 and PROD_2
    if ENV in [1, 2, 0]:
        default_exchange = Exchange('default', type='direct', durable=True)
    else:
        # default_exchange = Exchange('default', type='direct', durable=True)
        pass

    # General config:
    app.conf.update(
        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#result-backend
        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#database-url-examples
        # https://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#keeping-results
        # 1406, "Data too long for column 'result' at row 1" - it's not so important to keep it in DB
        result_backend=result_backend,
        # Content is picke for Python support:
        accept_content=['pickle', ],
        task_serializer='pickle',
        result_serializer='pickle',  # https://docs.celeryproject.org/en/master/userguide/calling.html#calling-serializers
        # Show when task is STARTED status
        result_extended=True,  # https://docs.celeryproject.org/en/master/userguide/configuration.html#result-extended
        # Do not set! Or logic will not wait of task OK: # task_ignore_result=True,
        task_track_started=True,
        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#beat-scheduler
        beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
        # result_backend='django-db',
        database_engine_options={'pool_timeout': 90},
        # http://docs.celeryproject.org/en/latest/userguide/configuration.html#worker-prefetch-multiplier
        worker_prefetch_multiplier=1,  # NOTE: Do not rely on celery queue no more, use rabbitmq queues instead!
        worker_concurrency=1,  # https://docs.celeryproject.org/en/master/userguide/configuration.html#worker-concurrency
        # Useful
        # https://docs.celeryproject.org/en/master/userguide/configuration.html#worker-log-format
        worker_timer_precision=1.0,  # https://docs.celeryproject.org/en/master/userguide/configuration.html#worker-timer-precision
        broker_heartbeat=10.0,  # https://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_heartbeat
        broker_heartbeat_checkrate=2.0,
    )
    # use for PROD_2, and NEW PROD_1
    if ENV in [1, 2, 0]:
        print(f"Load setup for Celery 5.3.4")
        """ This is setup for new celery=5.3.4 """
        app.autodiscover_tasks()  # Load task modules from all registered Django app configs.
        app.conf.update(
            # Workers setup: limit tasks and memory:
            # Memory limit - restart worker after reaching it.
            worker_max_memory_per_child=1024 * 100,
            # Restart worker each N tasks:
            worker_max_tasks_per_child=100,  # https://docs.celeryq.dev/en/stable/userguide/configuration.html#worker-max-tasks-per-child
            # The timeout in seconds (int/float) when waiting for a new worker process to start up.
            worker_proc_alive_timeout=5.0,

            # Do not RE-run task if worker dies during that task.
            task_acks_late=False,  # By Default # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_acks_late
            # When enabled messages for all tasks will be acknowledged even if they fail or time out.
            task_acks_on_failure_or_timeout=True,  # Default: Enabled https://docs.celeryq.dev/en/latest/userguide/configuration.html#std-setting-task_acks_on_failure_or_timeout
            # Do NOT cancel tasks on connection loss:
            # Disabled at: 16-07-2024
            # worker_cancel_long_running_tasks_on_connection_loss=True,
            # Enabled at: 16-07-2024
            task_reject_on_worker_lost=False,  # http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-reject-on-worker-lost

            # If enabled the worker pool can be restarted using the pool_restart remote control command.
            worker_pool_restarts=True,  # Default: Disabled by default.
            # Specify if remote control of the workers is enabled.
            worker_enable_remote_control=True,  # Default: Enabled by default. https://docs.celeryq.dev/en/latest/userguide/configuration.html#worker-enable-remote-control
            # In some cases a worker may be killed without proper cleanup, and the worker may have published a result before terminating.
            # This value specifies how long we wait for any missing results before raising a WorkerLostError exception.
            worker_lost_wait=20,  # Default: 10.0 seconds. https://docs.celeryq.dev/en/latest/userguide/configuration.html#worker-lost-wait

            # Broker setup:

            # Automatically try to establish the connection to the AMQP broker on Celery startup if it is unavailable.
            broker_connection_retry_on_startup=True,  # https://docs.celeryq.dev/en/latest/userguide/configuration.html#broker-connection-retry-on-startup
            broker_connection_retry=True,  # Default: Enabled. https://docs.celeryq.dev/en/latest/userguide/configuration.html#broker-connection-retry

            # Indefinitely retry to connect:
            broker_connection_max_retries=0,
            # Try each 4 seconds.
            broker_connection_timeout=4.0,
            # New in version 5.3.
            # Automatically try to re-establish the connection to the AMQP broker if any invalid response has been returned.
            # RECONNECT RabbitMQ: https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-channel-error-retry
            broker_channel_error_retry=True,  # Default: Disabled.
            # The maximum number of connections that can be open in the connection pool.
            broker_pool_limit=100,  # Default: 10. http://docs.celeryproject.org/en/latest/userguide/configuration.html#broker-pool-limit

            # Experiments

            # If enabled, a task-sent event will be sent for every task so tasks can be tracked before they’re consumed by a worker.
            task_send_sent_event=True,  # Default: Disabled by default.
            # Send task-related events so that tasks can be monitored using tools like flower. Sets the default value for the workers -E argument.
            worker_send_task_events=True,  # Default: Disabled by default. https://docs.celeryq.dev/en/latest/userguide/configuration.html#worker-send-task-events

            # The global default rate limit for tasks.
            # This value is used for tasks that doesn’t have a custom rate limit
            worker_disable_rate_limits=True,  # Default: No rate limit.https://docs.celeryq.dev/en/latest/userguide/configuration.html#task-default-rate-limit

            # http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-default-queue
            # Name of the default exchange to use when no custom exchange is specified for a key in the task_queues setting.
            # Default exchange type used when no custom exchange type is specified for a key in the task_queues setting.
            # task_default_exchange_type='direct',  # Default: "direct".
            task_default_queue='default',
            task_default_exchange='default',  # Single Exchange C.dq2 for all workers, but each worker has own queue: worker@host.dq2
            task_default_routing_key='default',
            task_default_exchange_type='direct',

            worker_direct=True,  # http://docs.celeryproject.org/en/latest/userguide/configuration.html#worker-direct

            # If enabled (default), any queues specified that aren’t defined in task_queues will be automatically created. See Automatic routing.
            task_create_missing_queues=True,  # Default: Enabled.

            # If set to True, result messages will be persistent. This means the messages won’t be lost after a broker restart.
            # result_persistent=True,  # https://docs.celeryq.dev/en/stable/userguide/configuration.html#result-persistent

            # Can be transient (messages not written to disk) or persistent (written to disk).
            task_default_delivery_mode='transient',  # Default: "persistent". https://docs.celeryproject.org/en/master/userguide/configuration.html#task-default-delivery-mode
        )
        """
        https://docs.celeryq.dev/en/latest/userguide/routing.html#manual-routing
        w_tku_upload@host.dq2
        w_deploy@host.dq2
        w_parsing@host.dq2
        w_routines@host.dq2
        anna@host.dq2
        berta@host.dq2
        carolina@host.dq2
        daria@host.dq2
        eduard@host.dq2
        ferdinand@host.dq2
        gerard@host.dq2
        helge@host.dq2
        karen@host.dq2
        roma@host.dq2
        sofie@host.dq2
    
        Read: https://medium.com/squad-engineering/two-years-with-celery-in-production-bug-fix-edition-22238669601d
        """

        # app.conf.task_queues = (
        #     Queue('default', routing_key='default'),
        #     Queue('w_tku_upload@host.dq2', routing_key='w_tku_upload@host.dq2'),
        #     Queue('w_deploy@host.dq2', routing_key='w_deploy@host.dq2'),
        #     Queue('w_parsing@host.dq2', routing_key='w_parsing@host.dq2'),
        #     Queue('w_routines@host.dq2', routing_key='w_routines@host.dq2'),
        #     Queue('anna@host.dq2', routing_key='anna@host.dq2'),
        #     Queue('berta@host.dq2', routing_key='berta@host.dq2'),
        #     Queue('carolina@host.dq2', routing_key='carolina@host.dq2'),
        #     Queue('daria@host.dq2', routing_key='daria@host.dq2'),
        #     Queue('eduard@host.dq2', routing_key='eduard@host.dq2'),
        #     Queue('ferdinand@host.dq2', routing_key='ferdinand@host.dq2'),
        #     Queue('gerard@host.dq2', routing_key='gerard@host.dq2'),
        #     Queue('helge@host.dq2', routing_key='helge@host.dq2'),
        #     Queue('karen@host.dq2', routing_key='karen@host.dq2'),
        #     Queue('roma@host.dq2', routing_key='roma@host.dq2'),
        #     Queue('sofie@host.dq2', routing_key='sofie@host.dq2'),
        # )
        print(f"<== Core Celery ==> New ENV: {hostname} ENV={ENV}; DB_NAME: {DB_NAME}")

    # use for PROD_1 this is OLD PROD_1, leave as refference and delete later.
    # if ENV == 2:
    #     """ celery=5.2.7 """
    #     app.autodiscover_tasks()  # Load task modules from all registered Django app configs.
    #     app.control.cancel_consumer('default', destination=workers)
    #     # http://docs.celeryproject.org/en/latest/userguide/configuration.html#broker-connection-timeout
    #     app.conf.update(
    #         task_send_sent_event=True,  # https://docs.celeryproject.org/en/master/userguide/configuration.html#task-send-sent-event
    #         worker_send_task_events=True,  # -E at worker service # http://docs.celeryproject.org/en/latest/userguide/configuration.html#events
    #         # Setting this to true allows the message to be re-queued instead, so that the task will execute again by the same worker, or another worker.
    #         task_reject_on_worker_lost=False,  # http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-reject-on-worker-lost
    #         # Maybe this should be disabled to allow workers to get ALL tasks in queue.
    #         task_acks_late=False,  # By Default # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_acks_late
    #         acks_late=False,  # http://docs.celeryproject.org/en/master/faq.html#faq-acks-late-vs-retry
    #         task_acks_on_failure_or_timeout=True,  # http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-acks-on-failure-or-timeout
    #         worker_disable_rate_limits=True,
    #         # http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-default-queue
    #         task_default_queue='default',
    #         task_default_exchange='default',
    #         task_default_routing_key='default',
    #         task_default_exchange_type='direct',
    #         # http://docs.celeryproject.org/en/latest/userguide/configuration.html#broker-connection-timeout
    #         broker_connection_timeout=4,
    #         broker_connection_max_retries=0,
    #         worker_enable_remote_control=True,  # https://docs.celeryproject.org/en/master/userguide/configuration.html#worker-enable-remote-control
    #         task_create_missing_queues=True,  # By Default  # http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-create-missing-queues
    #         worker_pool_restarts=True,
    #         broker_connection_retry=True,
    #         task_default_delivery_mode='transient',  # https://docs.celeryproject.org/en/master/userguide/configuration.html#task-default-delivery-mode
    #         worker_lost_wait=20,  # https://docs.celeryproject.org/en/master/userguide/configuration.html#worker-lost-wait
    #         worker_max_tasks_per_child=1000,  # https://docs.celeryproject.org/en/master/userguide/configuration.html#worker-max-tasks-per-child
    #         worker_max_memory_per_child=1024 * 100,  # 100MB
    #         broker_pool_limit=100,  # http://docs.celeryproject.org/en/latest/userguide/configuration.html#broker-pool-limit
    #         worker_direct=True,  # http://docs.celeryproject.org/en/latest/userguide/configuration.html#worker-direct
    #     )
    #     print(f"<== Core Celery ==> Legacy ENV: {hostname} ENV={ENV}; DB_NAME: {DB_NAME}")


# Startup celery or dummy
startup_celery()
