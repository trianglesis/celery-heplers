import argparse
import os
import subprocess
import atexit
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


def kill_runner(runner):
    runner.terminate()


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
                os.remove(f'{LOG_PATH}{os.sep}{worker}.log')

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
    # As many as workers we have
    pool = ThreadPool(processes=len(cmd_list))

    def kill_pool(err_msg):
        print(err_msg)
        pool.terminate()

    for cmd in cmd_list:
        if log_level == 'DEBUG':
            print(f"<==Celery WIN==> Run: {cmd}")

        pool.apply_async(workers_run,
                         kwds=dict(cmd=cmd, cwd=os.path.dirname(os.path.realpath(__file__))),
                         error_callback=kill_pool)

    pool.close()
    pool.join()
    pool.terminate()

    atexit.register(kill_runner, workers_run)
    exit()

    print(f'All run Took {time() - ts}')


def workers_run(**kwargs):
    cmd = kwargs.get('cmd')
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
    except Exception as e:
        msg = f"<==Celery WIN==> Error during operation for: {cmd} {e}"
        print(msg)


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
python celery_win.py --mode=start --log_level=INFO

Start only few workers:
python celery_win.py --mode=start --worker=alpha --log_level=DEBUG
python celery_win.py --mode=start --worker=alpha --worker=beta --log_level=DEBUG

"""
