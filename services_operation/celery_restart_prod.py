import os
from time import time
from queue import Queue
from threading import Thread
import argparse
import subprocess


CELERY_BIN = "/var/www/octopus/venv/bin/celery"
CELERY_APP = "octo.octo_celery:app"
CELERYD_PID_FILE = "/opt/celery/{PID}.pid"

CELERY_LOG_PATH = '/var/log/octopus'
CELERYD_LOG_FILE = "{PATH}/{LOG}.log"
CELERYD_LOG_LEVEL = "INFO"

CELERYD_OPTS = "--concurrency=1 -E"

CELERYD_NODES = [
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
    # 'lima@tentacle',
    # 'mike@tentacle',
    # 'november@tentacle',
    # 'oskar@tentacle',
    # 'papa@tentacle',
    # 'quebec@tentacle',
    # 'romeo@tentacle',
]

commands_list_start = "python3 {CELERY_BIN} multi start {celery_node} -A {CELERY_APP} --pidfile={CELERYD_PID_FILE} " \
                      "--logfile={CELERYD_LOG_FILE} --loglevel={CELERYD_LOG_LEVEL} {CELERYD_OPTS}"
commands_list_stop = "python3 {CELERY_BIN} multi kill {celery_node} -A {CELERY_APP} --pidfile={CELERYD_PID_FILE} " \
                     "--logfile={CELERYD_LOG_FILE} --loglevel={CELERYD_LOG_LEVEL} {CELERYD_OPTS}"
commands_list_restart = "python3 {CELERY_BIN} multi restart {celery_node} -A {CELERY_APP} --pidfile={CELERYD_PID_FILE} " \
                        "--logfile={CELERYD_LOG_FILE} --loglevel={CELERYD_LOG_LEVEL} {CELERYD_OPTS}"
commands_list_kill = "pkill -9 -f 'celery worker'"


def th_run(args):
    print(args)
    mode = args.mode
    print('Run th_run')

    stat = dict(
        start=commands_list_start,
        stop=commands_list_stop,
        restart=commands_list_restart,
        kill=commands_list_kill,
    )

    ts = time()
    thread_list = []
    th_out = []
    test_q = Queue()

    for celery_node in CELERYD_NODES:
        cmd_draft = stat[mode]
        cmd = cmd_draft.format(
            CELERY_BIN=CELERY_BIN,
            celery_node=celery_node,
            CELERY_APP=CELERY_APP,
            CELERYD_PID_FILE=CELERYD_PID_FILE.format(PID=celery_node),
            CELERYD_LOG_FILE=CELERYD_LOG_FILE.format(PATH=CELERY_LOG_PATH, LOG=celery_node),
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
    print(f'All run Took {time() - ts} Out {th_out}')


def worker_restart(**args_d):
    cmd = args_d.get('cmd')
    test_q = args_d.get('test_q')
    cwd = "/var/www/octopus/"
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
parser.add_argument('-m', '--mode', choices=['start', 'stop', 'restart', 'kill'], required=True)
th_run(parser.parse_args())
