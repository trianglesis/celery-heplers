import argparse
import os
import subprocess
from queue import Queue
from threading import Thread
from time import time


"""
Setup here your:

ENV - path to python virtual env, from the directory where you store this file. Best - root dir of your project.
APP - path to custom celery options file
LOG_PATH - where put logs, better to put near the folder you're working now.
SCHEDULE - if you set django_celery_beat schedule for BEAT worker.
workers - list of ALL workers you may need, for keeping CMD line shorter

"""

ENV = f'win_venv{os.sep}Scripts{os.sep}activate.bat'
APP = 'octo.octo_celery:app'
LOG_PATH = 'Y_log'

SCHEDULE = '--schedule=django_celery_beat.schedulers:DatabaseScheduler'

workers = [
    "w_development@tentacle",
    "w_tku_upload@tentacle",
    'w_deploy@tentacle',
    "w_parsing@tentacle",
    "w_routines@tentacle",
    "alpha@tentacle",
    "beta@tentacle",
    "charlie@tentacle",
    "delta@tentacle",
    "echo@tentacle",
    "foxtrot@tentacle",
    "golf@tentacle",
    'hotel@tentacle',
    'india@tentacle',
    'juliett@tentacle',
    'kilo@tentacle',
    'lima@tentacle',
    'mike@tentacle',
    'november@tentacle',
    'oscar@tentacle',
    'papa@tentacle',
    'quebec@tentacle',
    'romeo@tentacle',
]


def th_run(args):
    print(args)
    mode = args.mode

    # Set log level, and reuse DEBUG for this script too
    log_level = args.log_level
    if not log_level or log_level is None:
        log_level = 'INFO'

    # Pass a list of workers OR use default:
    worker_list = args.worker
    if not worker_list or worker_list is None:
        worker_list = workers

    if log_level == 'DEBUG':
        print(f'<==Celery WIN==> Will "{mode}" celery workers:\n\t{worker_list}')

    cmd_list = []
    # Start or stop or kill list of workers:
    if mode == 'start':
        for worker in worker_list:
            cmd_f = f"{ENV} && celery -A {APP} worker --loglevel={log_level} --concurrency=1 -E -n {worker}@tentacle --logfile={LOG_PATH}{os.sep}{worker}.log"
            cmd_list.append(cmd_f)

    # Only start beat as separated process:
    # win_venv\Scripts\activate.bat && celery beat --schedule=django_celery_beat.schedulers:DatabaseScheduler
    elif mode == 'beat':
        cmd_f = f"{ENV} && celery -A {APP} beat --loglevel={log_level} --logfile={LOG_PATH}{os.sep}beat.log {SCHEDULE}"
        cmd_list.append(cmd_f)

    else:
        print(f"<==Celery WIN==> MODE is not supported: {mode}")

    if log_level == 'DEBUG':
        print(f"<==Celery WIN==> Composed command list: {cmd_list}")

    # Now run commands each in separate thread
    ts = time()
    thread_list = []
    th_out = []
    queue = Queue()

    for cmd in cmd_list:
        if log_level == 'DEBUG':
            print(f"<==Celery WIN==> Run: {cmd}")
        th_name = f"Run CMD: {cmd}"
        try:
            test_thread = Thread(target=workers_run, name=th_name, kwargs=dict(cmd=cmd, queue=queue, cwd=os.path.dirname(os.path.realpath(__file__))))
            test_thread.start()
            thread_list.append(test_thread)
        except Exception as e:
            msg = "Thread fail with error: {}".format(e)
            print(msg)
            return msg
    # Execute threads:
    for th in thread_list:
        th.join()
        th_out.append(queue.get())
    print(f'All run Took {time() - ts} Out {th_out}')


def workers_run(**kwargs):
    cmd = kwargs.get('cmd')
    queue = kwargs.get('queue')
    cwd = kwargs.get('cwd')
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
        queue.put(run_results)
    except Exception as e:
        msg = f"<==Celery WIN==> Error during operation for: {cmd} {e}"
        queue.put(msg)
        print(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-m', '--mode', choices=['start', 'beat'], required=True)
    parser.add_argument('-w', '--worker', action='append')
    parser.add_argument('-l', '--log_level', choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'])
    th_run(parser.parse_args())


"""
This is the simplest script for celery workers run on windows. Nothing else.
Exit or kill by Ctrl+C and that's all.

Start beat only (only as separate console or instance):
python celery_win.py --mode=beat

Start ALL workers available: 
python celery_win.py --mode=start --log_level=DEBUG

Start only few workers:
python celery_win.py --mode=start --worker=alpha --worker=beta --log_level=DEBUG

"""
