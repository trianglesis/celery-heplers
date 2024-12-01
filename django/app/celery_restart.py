import argparse
import os
import socket
import subprocess
from queue import Queue
from threading import Thread
from time import time

from core.credentials import CeleryCreds, HostnamesSupported

hostname = socket.gethostname()

# 0 is DEV
# 1 is Prod1
# 2 is Prod2
ENV = 0
print("\n\n\n")
print("<== Celery Worker Service ==> Initialize...")
# LOCAL DEV
if hostname == HostnamesSupported.LOCAL_DEV_HOST:
    ENV = 0
    CELERY_BIN = "/home/user/projects/prod1/venv/bin/celery"
    cwd = "/mnt/d/Projects/prod1/"
    CELERYD_PID_FILE = "/home/user/{PID}.pid"
    CELERY_LOG_PATH = '/mnt/d/Projects/prod1/Y_log/celery'
    workers = CeleryCreds.WSL_WORKERS
    CELERYD_LOG_LEVEL = "INFO"
    print(f"<== Celery Worker Service ==> LOCAL DEV ENV: {hostname} ENV={ENV} CELERY_BIN:{CELERY_BIN} workers: {workers}")
# prod1
elif hostname == HostnamesSupported.prod1:
    ENV = 1
    CELERY_BIN = "/var/www/prod1/venv/bin/celery"
    cwd = "/var/www/prod1/"
    CELERYD_PID_FILE = "/opt/celery/{PID}.pid"
    CELERY_LOG_PATH = '/var/log/prod/celery'
    workers = CeleryCreds.prod1_WORKERS
    CELERYD_LOG_LEVEL = "INFO"
    print(f"<== Celery Worker Service ==> prod1 DEV ENV: {hostname} ENV={ENV} CELERY_BIN:{CELERY_BIN} workers: {workers}")
# prod2
else:
    ENV = 2
    CELERY_BIN = "/var/www/prod1/venv/bin/celery"
    cwd = "/var/www/prod1/"
    CELERYD_PID_FILE = "/opt/celery/{PID}.pid"
    CELERY_LOG_PATH = '/var/log/prod/celery'
    workers = CeleryCreds.prod2_WORKERS
    CELERYD_LOG_LEVEL = "INFO"
    print(f"<== Celery Worker Service ==> prod2: {hostname} ENV={ENV} CELERY_BIN:{CELERY_BIN} workers: {workers}")

CELERY_APP = "octo.octo_celery:app"
CELERYD_LOG_FILE = "{PATH}/{LOG}%I.log"

# https://docs.celeryq.dev/en/stable/reference/cli.html#cmdoption-celery-worker-max-tasks-per-child
# https://docs.celeryq.dev/en/stable/reference/cli.html#cmdoption-celery-worker-max-memory-per-child
CELERYD_OPTS = "--concurrency=1 -E"
CELERYD_NODES = workers

# NOTE: Use gdb python for debug!
commands_list_start = "python3 {CELERY_BIN} multi start " \
                      "{celery_node} -A {CELERY_APP} " \
                      "--pidfile={CELERYD_PID_FILE} " \
                      "--logfile={CELERYD_LOG_FILE} " \
                      "--loglevel={CELERYD_LOG_LEVEL} --concurrency=1 -E"

commands_list_stop = "python3 {CELERY_BIN} multi kill " \
                     "{celery_node} -A {CELERY_APP} " \
                     "--pidfile={CELERYD_PID_FILE} " \
                     "--logfile={CELERYD_LOG_FILE} " \
                     "--loglevel={CELERYD_LOG_LEVEL}"

commands_list_restart = "python3 {CELERY_BIN} multi restart " \
                        "{celery_node} -A {CELERY_APP} " \
                        "--pidfile={CELERYD_PID_FILE}"

commands_list_kill = "pkill -9 -f 'octo.octo_celery:app worker " \
                     "--pidfile={CELERYD_PID_FILE}'"


def th_run(args):
    # print(args)
    mode = args.mode
    worker_list = args.worker
    print(f'Run celery commands: {mode}, {worker_list}')

    stat = dict(
        start=commands_list_start,
        stop=commands_list_stop,
        restart=commands_list_restart,
        kill=commands_list_kill,
        kill_queues=commands_list_kill,
    )

    ts = time()
    thread_list = []
    th_out = []
    test_q = Queue()

    if worker_list:
        workers = [worker + "@tentacle" for worker in worker_list]
    else:
        workers = CELERYD_NODES

    for celery_node in workers:
        cmd_draft = stat[mode]
        cmd = cmd_draft.format(
            CELERY_BIN=CELERY_BIN,
            celery_node=celery_node,
            CELERY_APP=CELERY_APP,
            CELERYD_PID_FILE=CELERYD_PID_FILE.format(PID=celery_node),
            CELERYD_LOG_FILE=CELERYD_LOG_FILE.format(PATH=CELERY_LOG_PATH, LOG=celery_node.replace("@tentacle", "")),  # Do not use @tentacle in the name of logfile.
            CELERYD_LOG_LEVEL=CELERYD_LOG_LEVEL,
            CELERYD_OPTS=CELERYD_OPTS,
        )
        print(f"Run: {cmd}")
        args_d = dict(cmd=cmd, test_q=test_q)
        th_name = f"Run CMD: {cmd}"
        try:
            test_thread = Thread(target=worker_restart, name=th_name, kwargs=args_d)
            test_thread.start()
            thread_list.append(test_thread)
        except Exception as e:
            msg = "Thread test fail with error: {}".format(e)
            print(msg)
            return msg
    # Execute threads:
    for th in thread_list:
        th.join()
        th_out.append(test_q.get())

    if ENV == 1:
        if mode == 'start':
            pass
            # print(f"Re-add queues for: {workers}")
            # worker_queues = WorkerOperations.worker_restart(workers)
            # print(worker_queues)

    print(f'All run Took {time() - ts} Out {th_out}')


def worker_restart(**args_d):
    cmd = args_d.get('cmd')
    test_q = args_d.get('test_q')
    my_env = os.environ.copy()
    run_results = []
    try:
        run_cmd = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=cwd,
                                   env=my_env,
                                   shell=True,
                                   )
        # run_cmd.wait()
        stdout, stderr = run_cmd.communicate()
        stdout, stderr = stdout.decode('utf-8'), stderr.decode('utf-8')
        run_results.append({'stdout': stdout, 'stderr': stderr})
        test_q.put(run_results)
    except Exception as e:
        msg = f"<=run_subprocess=> Error during operation for: {cmd} {e}"
        test_q.put(msg)
        print(msg)


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-m', '--mode', choices=['start', 'stop', 'restart', 'kill', 'kill_queues'], required=True)
parser.add_argument('-w', '--worker', action='append')
th_run(parser.parse_args())

"""
Doc: https://docs.celeryq.dev/en/stable/userguide/workers.html#starting-the-worker

# Using systemd service: do not use restart!
systemctl stop celery.service && systemctl start celery.service
systemctl stop celerybeat.service && systemctl start celerybeat.service

STOP:
python celery_restart.py --mode=kill

# STOP AND START:
python celery_restart.py --mode=kill; python celery_restart.py --mode=start

# One worker or few:
python celery_restart.py --mode=kill --worker=alpha; python celery_restart.py --mode=start --worker=alpha
python celery_restart.py --mode=kill --worker=beta; python celery_restart.py --mode=start --worker=beta
python celery_restart.py --mode=kill --worker=echo; python celery_restart.py --mode=start --worker=echo
# prod1
python celery_restart.py --mode=kill --worker=berta; python celery_restart.py --mode=start --worker=berta
python celery_restart.py --mode=kill --worker=eduard; python celery_restart.py --mode=start --worker=eduard
python celery_restart.py --mode=kill --worker=anna; python celery_restart.py --mode=start --worker=anna


# Few
python celery_restart.py --mode=kill \
    --worker=alpha \
    --worker=beta \
    --worker=echo; \
python celery_restart.py --mode=start \
    --worker=alpha \
    --worker=beta \
    --worker=echo


python celery_restart.py --mode=kill --worker=w_parsing; python celery_restart.py --mode=start --worker=w_parsing
python celery_restart.py --mode=kill --worker=w_deploy; python celery_restart.py --mode=start --worker=w_deploy
python celery_restart.py --mode=kill --worker=w_tku_upload; python celery_restart.py --mode=start --worker=w_tku_upload
python celery_restart.py --mode=kill --worker=w_routines; python celery_restart.py --mode=start --worker=w_routines

# Few
python celery_restart.py --mode=kill \
    --worker=w_tku_upload \
    --worker=w_parsing \
    --worker=w_routines \
    --worker=w_tku_upload; \
python celery_restart.py --mode=start \
    --worker=w_routines \
    --worker=w_tku_upload

# All test workers:
python celery_restart.py --mode=kill \
    --worker=carolina \
    --worker=daria \
    --worker=ferdinand \
    --worker=gerard \
    --worker=helge \
    --worker=karen \
    --worker=roma \
    --worker=sofie; \
python celery_restart.py --mode=start \
    --worker=carolina \
    --worker=daria \
    --worker=ferdinand \
    --worker=gerard \
    --worker=helge \
    --worker=karen \
    --worker=roma \
    --worker=sofie

python celery_restart.py --mode=kill --worker=daria; python celery_restart.py --mode=start --worker=daria
python celery_restart.py --mode=kill --worker=roma; python celery_restart.py --mode=start --worker=roma
python celery_restart.py --mode=kill --worker=sofie; python celery_restart.py --mode=start --worker=sofie

# For WIN
python celery_restart.py --mode=kill --worker=beat; python celery_restart.py --mode=beat --worker=beat

RabbitMQ:
rabbitmqctl list_queues -p tentacle

prod1:
sudo rabbitmqctl delete_queue -p tentacle default; \
    sudo rabbitmqctl delete_queue -p tentacle anna@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle berta@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle carolina@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle daria@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle eduard@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle ferdinand@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle gerard@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle helge@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle karen@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle roma@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle sofie@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle w_tku_upload@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle w_deploy@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle w_parsing@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle w_routines@tentacle.dq2


prod2:
sudo rabbitmqctl delete_queue -p tentacle alpha@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle beta@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle charlie@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle delta@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle echo@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle foxtrot@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle golf@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle hotel@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle india@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle juliett@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle kilo@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle lima@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle mike@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle november@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle oscar@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle papa@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle quebec@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle romeo@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle sierra@tentacle.dq2

Common:
sudo rabbitmqctl delete_queue -p tentacle w_tku_upload@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle w_deploy@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle w_parsing@tentacle.dq2; \
    sudo rabbitmqctl delete_queue -p tentacle w_routines@tentacle.dq2


DEBUG:
celery -A octo.octo_celery:app inspect active
celery -A octo.octo_celery:app inspect active_queues

# Run with DEBUG
celery -A octo.octo_celery:app worker --loglevel=DEBUG --concurrency=1 -E -n w_routines@tentacle
celery -A octo.octo_celery:app worker --loglevel=DEBUG --concurrency=1 -E -n carolina@tentacle --logfile=/var/log/prod2/celery/carolina@tentacle.log

# Kill and start worker separately for debug:
celery multi kill w_parsing@tentacle --pidfile=/opt/celery/w_parsing@tentacle.pid --logfile=/var/log/prod2/celery/w_parsing@tentacle.log
celery -A octo.octo_celery:app worker --loglevel=DEBUG --concurrency=1 -E -n w_parsing@tentacle --pidfile=/opt/celery/w_parsing@tentacle.pid --logfile=/var/log/prod2/celery/w_parsing@tentacle.log


Use flower for debug:
pip install flower
celery -A octo.octo_celery:app flower --address='0.0.0.0'
celery -A octo.octo_celery:app report


rabbitmqctl delete_queue -p tentacle Consumer-anna@tentacle; \
    rabbitmqctl delete_queue -p tentacle Consumer-w_routines@tentacle; \
    rabbitmqctl delete_queue -p tentacle Consumer-w_parsing@tentacle; \
    rabbitmqctl delete_queue -p tentacle Consumer-w_tku_upload@tentacle; \
    rabbitmqctl delete_queue -p tentacle Consumer-roma@tentacle; \
    rabbitmqctl delete_queue -p tentacle Consumer-sofie@tentacle; \
    rabbitmqctl delete_queue -p tentacle Consumer-w_deploy@tentacle
"""
