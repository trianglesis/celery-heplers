import os
from time import time
from queue import Queue
from threading import Thread
import argparse
import subprocess

"""
Use this to start/stop/restart celery, it's much more flexible.
TODO: Add restart for single worker only? Or maybe this is not the best approach?
TODO: Add some sort of log rotate?
"""

# CELERY_BIN = "/var/www/octopus/venv/bin/celery"
CELERY_APP = "octo.octo_celery:app"
CELERYD_PID_FILE = "/opt/celery/{PID}.pid"
CELERYD_LOG_FILE = "{PATH}/{LOG}.log"
CELERYD_LOG_LEVEL = "INFO"
CELERYD_OPTS = "--concurrency=1 -E"

CELERYD_NODES = [
    # "w_development@tentacle",
    "w_parsing@tentacle",
    "w_routines@tentacle",
    "alpha@tentacle",
    # "beta@tentacle",
    # "charlie@tentacle",
    # "delta@tentacle",
    # "echo@tentacle",
    # "foxtrot@tentacle",
    # "golf@tentacle",
    # 'hotel@tentacle',
    # 'india@tentacle',
    # 'juliett@tentacle',
    # 'kilo@tentacle',
    # 'lima@tentacle',
    # 'mike@tentacle',
    # 'november@tentacle',
    # 'oskar@tentacle',
    # 'papa@tentacle',
    # 'quebec@tentacle',
    # 'romeo@tentacle',
]

# celery -A octo worker --loglevel=info
# celery -A octo w_parsing@tentacle --pidfile=/opt/celery/w_parsing@tentacle.pid --logfile=/var/log/octopus/w_parsing@tentacle.log --loglevel=info --concurrency=1 -E
commands_list_start = "{CELERY_BIN} multi start {celery_node} -A {CELERY_APP} --pidfile={CELERYD_PID_FILE} --logfile={CELERYD_LOG_FILE} --loglevel={CELERYD_LOG_LEVEL} {CELERYD_OPTS}"
commands_list_kill = "pkill -9 -f 'celery worker'"

FLOWER_CMD = "{CELERY_BIN} flower --broker=amqp://octo_user:<PASSWORD>@localhost:5672/tentacle --broker_api=http://octo_user:<PASSWORD>@localhost:15672/api/"
FLOWER_KILL = "pkill -9 -f 'celery flower'"

BEAT_CMD = "{CELERY_BIN} beat -A octo.octo_celery:app --detach --pidfile=/opt/celery/beat.pid --logfile={PATH}/beat.log --loglevel=info --schedule=--schedule=django_celery_beat.schedulers:DatabaseScheduler"
BEAT_KILL = "pkill -9 -f 'celery beat'"


def th_run(args):
    print(args)
    env = args.env
    commands_list_ready = []  # All composed commands to be executed

    # REQUIRED:
    # Assign Celery bin paths for different dev environments:
    celery_bin = dict(
        wsl_work='venv/bin/celery',
        wsl_home='venv/bin/celery',
        octopus='/var/www/octopus/venv/bin/celery',
        lobster='/var/www/octopus/venv/bin/celery',
    )
    CELERY_BIN = celery_bin[env]
    # TODO: Use same? Later remove?
    # Assign Celery log paths for different dev environments:
    celery_logs = dict(
        wsl_work='/var/log/octopus',
        wsl_home='/var/log/octopus',
        octopus='/var/log/octopus',
        lobster='/var/log/octopus',
    )
    CELERY_LOG_PATH = celery_logs[env]

    # Working dir:
    cwd_path = dict(
        wsl_work='/mnt/d/Projects/PycharmProjects/lobster/',
        wsl_home='/mnt/d/Projects/PycharmProjects/lobster/',
        octopus='/var/www/octopus/',
        lobster='/var/www/octopus/',
    )

    if args.server:
        if 'start' in args.server:
            print("Start WEB Server")
            server_cmd = 'python3 manage.py runserver'
            commands_list_ready.append(server_cmd)
        elif 'kill' in args.server:
            print("Kill Web Server")
            server_cmd = "pkill -9 -f 'manage.py runserver'"
            commands_list_ready.append(server_cmd)

    if args.celery:
        if 'start' in args.celery:
            print("Start celery workers!")
            celery_cmd = commands_list_start
            for celery_node in CELERYD_NODES:
                cmd = celery_cmd.format(
                    CELERY_BIN=CELERY_BIN,
                    celery_node=celery_node,
                    CELERY_APP=CELERY_APP,
                    CELERYD_PID_FILE=CELERYD_PID_FILE.format(PID=celery_node),
                    CELERYD_LOG_FILE=CELERYD_LOG_FILE.format(PATH=CELERY_LOG_PATH, LOG=celery_node),
                    CELERYD_LOG_LEVEL=CELERYD_LOG_LEVEL,
                    CELERYD_OPTS=CELERYD_OPTS,
                )
                commands_list_ready.append(cmd)
        elif 'kill' in args.celery:
            print("Kill celery workers!")
            celery_cmd = commands_list_kill
            commands_list_ready.append(celery_cmd)
        else:
            # Later add restart for single worker if needed?
            print("No celery actions!")

    if args.beat:
        if 'start' in args.beat:
            print("Start Celery Beat")
            beat_cmd = BEAT_CMD.format(CELERY_BIN=CELERY_BIN, PATH=CELERY_LOG_PATH)
            commands_list_ready.append(beat_cmd)
        elif 'kill' in args.beat:
            print("Kill Celery Beat")
            beat_cmd = BEAT_KILL
            commands_list_ready.append(beat_cmd)

    if args.flower:
        if 'start' in args.flower:
            print("Start Flower")
            flower_cmd = FLOWER_CMD.format(CELERY_BIN=CELERY_BIN)
            commands_list_ready.append(flower_cmd)
        elif 'kill' in args.flower:
            print("Kill Flower")
            flower_cmd = FLOWER_KILL
            commands_list_ready.append(flower_cmd)

    ts = time()
    thread_list = []
    th_out = []
    test_q = Queue()

    for cmd in commands_list_ready:
        print(f"Run: {cmd}")
        args_d = dict(cmd=cmd, test_q=test_q, cwd=cwd_path[env])
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
    cwd = args_d.get('cwd')
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
parser.add_argument('-s', '--server', choices=['start', 'kill'])
parser.add_argument('-C', '--celery', choices=['start', 'kill'])
parser.add_argument('-B', '--beat', choices=['start', 'kill'])
parser.add_argument('-F', '--flower', choices=['start', 'kill'])
parser.add_argument('-e', '--env', choices=['wsl_work', 'wsl_home', 'octopus', 'lobster'], required=True)
th_run(parser.parse_args())

"""
On WSL:
https://www.jetbrains.com/help/pycharm/using-wsl-as-a-remote-interpreter.html
/usr/sbin/sshd -D

su user then activate env, then run

Run celery and flower as separate, due flower will use std:
source /var/www/lobster/venv/bin/activate
python celery_restart_DEV.py --env=wsl_work --celery=kill; python celery_restart_DEV.py --env=wsl_work --celery=start
python celery_restart_DEV.py --env=wsl_work --beat=kill; python celery_restart_DEV.py --env=wsl_work --beat=start
python celery_restart_DEV.py --env=wsl_work --flower=kill; python celery_restart_DEV.py --env=wsl_work --flower=start

On scheduler:
C:\Windows\System32\bash.exe -c "cd ~/lobster; source venv/bin/activate; python celery_restart_DEV.py --env=wsl_home --flower=kill; python celery_restart_DEV.py --env=wsl_home --flower=start"
C:\Windows\System32\bash.exe -c "cd ~/lobster; source venv/bin/activate; python celery_restart_DEV.py --env=wsl_home --celery=kill; python celery_restart_DEV.py --env=wsl_home --celery=start"
C:\Windows\System32\bash.exe -c "cd ~/lobster; source venv/bin/activate; python celery_restart_DEV.py --env=wsl_home --beat=kill; python celery_restart_DEV.py --env=wsl_home --beat=start"
venv/bin/python celery_restart_DEV.py --env=wsl_work --celery=start --server=start
"""