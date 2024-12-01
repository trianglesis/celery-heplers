"""
This is credentials file.
Only store all empty variables here. Fill it later, locally.
"""


class HostnamesSupported:
    """
    All possible expected hostnames where PROD_1 code might run.
    """
    # PROD_1
    PROD_1 = 'PROD_1.example.com'
    PROD_1_FQDN = 'PROD_1.example.com'
    PROD_1_HOSTNAME = 'PROD_1'
    PROD_1_IP = '1.2.3.4'
    # PROD_2
    PROD_2 = 'PROD_2.example.com'
    PROD_2_FQDN = 'PROD_2.example.com'
    PROD_2_HOSTNAME = 'PROD_2'
    PROD_2_IP = '1.2.3.5'
    # Local
    LOCAL_DEV_HOST = 'wsl-local'

class DjangoCreds:
    SECRET_KEY = 'DJANGO_SECRET'
    EMAIL_HOST = 'mail.example.com'
    mails = dict(
        admin='ADMIN_EMAIL',
    )
    ADMINS = [('NAME', 'ADMIN_EMAIL')]


class HostCreds:
    # PROD_1
    PROD_1_HOSTNAME = HostnamesSupported.PROD_1_HOSTNAME
    PROD_1_FQDN = HostnamesSupported.PROD_1
    PROD_1_IP = HostnamesSupported.PROD_1_IP
    PROD_1_HOSTEMAIL = 'PROD_1@example.com'
    PROD_1_SITE_SHORT_NAME = 'PROD_1'
    PROD_1_EMAIL_HOST_USER = 'PROD_1@example.com'
    PROD_1_EMAIL_HOST_PASSWORD = 'PROD_1_EMAIL_HOST_PASSWORD'

    # PROD_2
    PROD_2_HOSTNAME = HostnamesSupported.PROD_2_HOSTNAME
    PROD_2_FQDN = HostnamesSupported.PROD_2
    PROD_2_IP = HostnamesSupported.PROD_2_IP
    PROD_2_HOSTEMAIL = 'PROD_2@example.com'
    PROD_2_SITE_SHORT_NAME = 'PROD_2'
    PROD_2_EMAIL_HOST_USER = 'PROD_2@example.com'
    PROD_2_EMAIL_HOST_PASSWORD = 'PROD_2_EMAIL_HOST_PASSWORD'

    LOCAL_HOSTNAME = 'LOCAL'
    LOCAL_FQDN = '127.0.0.1:8000'
    LOCAL_IP = '127.0.0.1'
    LOCAL_HOSTEMAIL = 'PROD_2@example.com'
    LOCAL_SITE_SHORT_NAME = 'Local'
    LOCAL_EMAIL_HOST_USER = 'PROD_2@example.com'
    LOCAL_EMAIL_HOST_PASSWORD = 'PASWD'


class MySQLDatabase:
    DB_ENGINE = 'django.db.backends.mysql'
    DB_USER = 'user'
    DB_HOST = 'localhost'  # Ethernet adapter vEthernet (WSL):
    DB_PORT = '3306'

    # Live and DEV versions
    DB_NAME_PROD_1 = 'PROD_1'
    DB_NAME_PROD_2 = 'PROD_2'
    DB_PASSWORD = 'PASSWD'
    # Local development use WSL IP!
    DB_HOST_WSL = 'IP_ADDR'
    OLD_DB_PASSWORD = 'PASSWD'


class RabbitMQCreds:
    # broker='librabbitmq://RABBITMQ_USER:RABBITMQ_PSWD@localhost:5672/tentacle'
    # broker='amqp://RABBITMQ_USER:RABBITMQ_PSWD@localhost:5672/tentacle'
    RABBITMQ_USER = 'user'
    RABBITMQ_PSWD = 'RABBITMQ_PSWD'

    BROKER = f'pyamqp://{RABBITMQ_USER}:{RABBITMQ_PSWD}@localhost:5672/tentacle'
    RABBITMQ_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PSWD}@localhost:5672/tentacle'


class CeleryCreds:

    DB_HOST = 'localhost'
    DB_HOST_Win = '127.0.0.1'
    DB_HOST_WSL = 'IP_ADDR'

    DB_USER = 'celery_backend'
    DB_PASSWORD = 'DB_PASSWORD'

    BACKEND = 'db+mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    RESULT_BACKEND = 'db+mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

    PROD_1_WORKERS = [
        "w_git@tentacle",
        "w_tku_upload@tentacle",
        "w_parsing@tentacle",
        "w_routines@tentacle",
        'w_deploy@tentacle',
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
        'sierra@tentacle',
        # 'tango@tentacle',
        # 'uniform@tentacle',
    ]

    PROD_2_WORKERS = [
        "w_git@tentacle",
        # "w_development@tentacle",
        "w_tku_upload@tentacle",
        'w_deploy@tentacle',
        "w_parsing@tentacle",
        "w_routines@tentacle",
        # Development nodes
        'anna@tentacle',
        'berta@tentacle',
        'carolina@tentacle',
        'daria@tentacle',
        'eduard@tentacle',
        'ferdinand@tentacle',
        'gerard@tentacle',
        'helge@tentacle',
        # 'ida@tentacle',
        # 'jean@tentacle',
        'karen@tentacle',
        # 'lena@tentacle',
        # 'maria@tentacle',
        # 'nicolas@tentacle',
        # 'olga@tentacle',
        # 'paul@tentacle',
        # 'queen@tentacle',
        'roma@tentacle',
        'sofie@tentacle',
        # 'thomas@tentacle',
        # 'ursula@tentacle',
        # 'victor@tentacle',
        # 'wilson@tentacle',
        # 'xavier@tentacle',
        # 'yolanda@tentacle',
        # 'zuzana@tentacle',
    ]

    WSL_WORKERS = [
        "w_git@tentacle",
        'w_deploy@tentacle',
        # Only tests:
        "w_parsing@tentacle",
        "w_routines@tentacle",
        'carolina@tentacle',
        'daria@tentacle',
        'helge@tentacle',
        # Upload:
        # "w_tku_upload@tentacle",
        # 'anna@tentacle',
        # 'berta@tentacle',
        # 'eduard@tentacle',
    ]