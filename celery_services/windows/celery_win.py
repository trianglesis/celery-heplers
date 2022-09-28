import argparse
import os
import subprocess
import atexit
import signal
import sys
from multiprocessing import Queue
from multiprocessing.pool import ThreadPool
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
LOG_PATH = f'Y_log{os.sep}celery'

SCHEDULE = '--schedule=django_celery_beat.schedulers:DatabaseScheduler'

workers = [
    # "w_development",
    # "w_tku_upload",
    # 'w_deploy',
    "w_parsing",
    "w_routines",
    "alpha",
    "beta",
    # "charlie",
    # "delta",
    # "echo",
    # "foxtrot",
    # "golf",
    # 'hotel',
    # 'india',
    'juliett',
    'kilo',
    # 'lima',
    # 'mike',
    # 'november',
    # 'oscar',
    # 'papa',
    # 'quebec',
    # 'romeo',
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

    if args.wipe_logs:
        if log_level == 'DEBUG':
            print(f'<==Celery WIN==> Will wipe all previously generated logs.')
            for worker in worker_list:
                log_f = f'{LOG_PATH}{os.sep}{worker}.log'
                if os.path.exists(log_f):
                    os.remove(log_f)

    cmd_dict = dict()
    # Start or stop or kill list of workers:
    if mode == 'start':
        for worker in worker_list:
            cmd_f = f"{ENV} && celery -A {APP} worker --loglevel={log_level} --concurrency=1 -E -n {worker}@tentacle --logfile={LOG_PATH}{os.sep}{worker}.log"
            cmd_dict.update({worker: cmd_f})

    # Only start beat as separated process:
    # win_venv\Scripts\activate.bat && celery beat --schedule=django_celery_beat.schedulers:DatabaseScheduler
    elif mode == 'beat':
        cmd_f = f"{ENV} && celery -A {APP} beat --loglevel={log_level} --logfile={LOG_PATH}{os.sep}beat.log {SCHEDULE}"
        cmd_dict.update({"beat": cmd_f})

    else:
        print(f"<==Celery WIN==> MODE is not supported: {mode}")

    if log_level == 'DEBUG':
        print(f"<==Celery WIN==> Composed command list:")
        for worker, cmd in cmd_dict.items():
            print(f'{worker}: "{cmd}" ')

    # Execute:
    multi(cmd_dict)


def multi(cmd_dict):
    # Now run commands each in separate thread
    ts = time()
    outputs = []
    # As many as workers we have
    print(f"<==Celery WIN==> Process pools: {len(cmd_dict)}")
    pool = ThreadPool(processes=len(cmd_dict))
    queue = Queue()

    def kill_pool(err_msg):
        print(err_msg)
        pool.terminate()

    for worker, cmd in cmd_dict.items():
        print(f"<==Celery WIN==> Run pool.apply_async: {cmd}")
        pool.apply_async(workers_run,
                         kwds=dict(queue=queue, cmd=cmd, worker=worker),
                         error_callback=kill_pool)
    try:
        pool.close()
        pool.join()
    except KeyboardInterrupt as e:
        out = [queue.get() for i in range(len(cmd_dict))]
        for o in out:
            outputs.append(o)

        # Any other finish condition?
        pool.terminate()

        print(f"<==Celery WIN Exit==> Keyboard interrupt - kill pool!"
              f"\n\tWorked for: {time() - ts}"
              f"\n\tCommand out: {outputs}"
              f"\n\tException: {e}")

    print(f'Finally: All run Took {time() - ts}')
    return None


def workers_run(**kwargs):
    queue = kwargs.get('queue')
    cmd = kwargs.get('cmd')
    worker = kwargs.get('worker')

    cwd = os.path.dirname(os.path.realpath(__file__))
    my_env = os.environ.copy()
    run_cmd = None

    try:
        run_cmd = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,  # Redirect, but do not show
                                   stderr=subprocess.PIPE,
                                   cwd=cwd,
                                   env=my_env,
                                   shell=True,
                                   )

        _, stderr = run_cmd.communicate()
        stderr = stderr.decode('utf-8')

        if stderr and 'Hitting Ctrl+C again' in stderr:
            print(f"<==Celery WIN Exit==> '{worker}' is asking for Ctrl+C! Sending: signal.CTRL_C_EVENT")
            os.kill(run_cmd.pid, signal.CTRL_C_EVENT)

            print(f"<==Celery WIN Exit==> '{worker}' Ensure killing process with: signal.SIGINT and complete kill")
            run_cmd.send_signal(signal.SIGINT)
            run_cmd.kill()
            queue.put(f"MSG: '{worker}' Killed Celery worker on Keyboard interrupt.")

    except KeyboardInterrupt:
        print(f"<==Celery WIN Exit==> '{worker}' Keyboard interrupt - kill process")
        os.kill(run_cmd.pid, signal.CTRL_C_EVENT)
        run_cmd.send_signal(signal.SIGINT)
        run_cmd.kill()

        queue.put(f"'{worker}' - Keyboard interrupt - kill worker, Exception pass.")
        pass

    except Exception as e:
        print(f"<==Celery WIN Exit==> '{worker}' Error during operation: {e}")

        os.kill(run_cmd.pid, signal.CTRL_C_EVENT)
        run_cmd.send_signal(signal.SIGINT)
        run_cmd.kill()

        queue.put(f"{worker} - Error, kill worker")
        pass

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-m', '--mode', choices=['start', 'beat'], required=True)
    parser.add_argument('-w', '--worker', action='append')
    parser.add_argument('-l', '--log_level', choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'])
    parser.add_argument('--wipe_logs', action='store_true', help='Wipe previously generated logs content')
    th_run(parser.parse_args())

"""
This is the simplest script for celery workers run on windows. Nothing else.
Exit or kill by Ctrl+C and that's all.

Start beat only (only as separate console or instance):
python celery_win.py --mode=beat

Start ALL workers available:
python celery_win.py --mode=start --log_level=DEBUG --wipe_logs
python celery_win.py --mode=start --log_level=DEBUG
python celery_win.py --mode=start --log_level=INFO --wipe_logs

Start only few workers:
python celery_win.py --mode=start --worker=alpha --log_level=DEBUG
python celery_win.py --mode=start --worker=alpha --worker=beta --log_level=DEBUG --wipe_logs

"""
