##
"""

"""
import socket

from core.credentials import HostnamesSupported, HostCreds, MySQLDatabase, RabbitMQCreds

hostname = socket.gethostname()

# 0 is DEV
# 1 is PROD_2
# 2 is PROD_1
# 3 New PROD_1
ENV = 0
print("\n\n\n")
print("<== Config Cred ==> ENV Initialize...")
# LOCAL DEV
if hostname == HostnamesSupported.LOCAL_DEV_HOST:
    ENV = 0
    print(f"<== Config Cred ==> LOCAL DEV ENV: {hostname} ENV={ENV}")
# PROD_2
elif hostname == HostnamesSupported.PROD_2:
    ENV = 1
    print(f"<== Config Cred ==> PROD_2 DEV ENV: {hostname} ENV={ENV}")
# PROD_1
else:
    ENV = 2
    print(f"<== Config Cred ==> PROD_1: {hostname} ENV={ENV}")

class MySQLCredentials:
    # Database
    ENGINE = MySQLDatabase.DB_ENGINE
    USER = MySQLDatabase.DB_USER
    PASSWORD = MySQLDatabase.DB_PASSWORD
    HOST = MySQLDatabase.DB_HOST
    PORT = MySQLDatabase.DB_PORT
    # Local Dev machine
    if ENV == 0:
        NAME = MySQLDatabase.DB_NAME_PROD_2  # Use PROD_2
        HOST = MySQLDatabase.DB_HOST_WSL
        print(f"<== Config Cred WINDOWS ==> MySQL Localhost env MySQL host: {HOST} DB: {NAME}")
    # PROD_2
    elif ENV == 1:
        NAME = MySQLDatabase.DB_NAME_PROD_2  # Use PROD_2
        PASSWORD = MySQLDatabase.DB_PASSWORD
        print(f"<== Config Cred ==> MySQL PROD_2 env MySQL host: {HOST} DB: {NAME}")
    # PROD_1
    elif ENV == 2:
        NAME = MySQLDatabase.DB_NAME_PROD_1  # Use PROD_1
        PASSWORD = MySQLDatabase.DB_PASSWORD
        HOST = HostnamesSupported.PROD_1_FQDN
        print(f"<== Config Cred ==> MySQL PROD_1 env MySQL host: {HOST} DB: {NAME}")
    # Fallback
    else:
        print(f"ERROR MySQLCredentials: UNEXPECTED env HOSTNAME: {hostname}!!!")

class Credentials:
    # Site domain:
    PROD_2 = HostnamesSupported.PROD_2_FQDN
    PROD_1 = HostnamesSupported.PROD_1_FQDN

    rabbitmq_user = RabbitMQCreds.RABBITMQ_USER
    rabbitmq_pswd = RabbitMQCreds.RABBITMQ_PSWD

    # Site identity:
    # Local Dev machine
    if ENV == 0:
        HOSTNAME = HostnamesSupported.LOCAL_DEV_HOST
        FQDN = '127.0.0.1:8000'
        IP = '127.0.0.1'
        HOSTEMAIL = HostCreds.LOCAL_HOSTEMAIL  # Use PROD_2 for local dev
        SITE_SHORT_NAME = 'wsl-local'
        # EMAIL_HOST_USER = HostCreds.PROD_2_EMAIL_HOST_USER
        # EMAIL_HOST_PASSWORD = HostCreds.PROD_2_EMAIL_HOST_PASSWORD
        # Select corresponding DB Name:
        DB_NAME = MySQLDatabase.DB_NAME_PROD_2  # Use PROD_2
        print(f"<== Config Cred WINDOWS ==> Site env Local dev: {HOSTNAME}; FQDN: {FQDN}; DB_NAME: {DB_NAME}")
    # PROD_2
    elif ENV == 1:
        # PROD_2
        HOSTNAME = HostnamesSupported.PROD_2_HOSTNAME
        FQDN = HostCreds.PROD_2_FQDN
        IP = HostCreds.PROD_2_IP
        HOSTEMAIL = HostCreds.PROD_2_HOSTEMAIL
        SITE_SHORT_NAME = HostCreds.PROD_2_SITE_SHORT_NAME
        EMAIL_HOST_USER = HostCreds.PROD_2_EMAIL_HOST_USER
        EMAIL_HOST_PASSWORD = HostCreds.PROD_2_EMAIL_HOST_PASSWORD
        # Select corresponding DB Name:
        DB_NAME = MySQLDatabase.DB_NAME_PROD_2  # Use PROD_2
        print(f"<== Config Cred ==> Site env PROD_2: {HOSTNAME}; FQDN: {FQDN}; DB_NAME: {DB_NAME}")
    # PROD_1
    elif ENV == 2:
        # PROD_1
        HOSTNAME = HostnamesSupported.PROD_1_HOSTNAME
        FQDN = HostCreds.PROD_1_FQDN
        IP = HostCreds.PROD_1_IP
        HOSTEMAIL = HostCreds.PROD_1_HOSTEMAIL
        SITE_SHORT_NAME = HostCreds.PROD_1_SITE_SHORT_NAME
        EMAIL_HOST_USER = HostCreds.PROD_1_EMAIL_HOST_USER
        EMAIL_HOST_PASSWORD = HostCreds.PROD_1_EMAIL_HOST_PASSWORD
        # Select corresponding DB Name:
        DB_NAME = MySQLDatabase.DB_NAME_PROD_1  # Use PROD_1
        print(f"<== Config Cred ==> Site env PROD_2: {HOSTNAME}; FQDN: {FQDN}; DB_NAME: {DB_NAME}")
    # Fallback
    else:
        print(f"ERROR Credentials: UNEXPECTED env HOSTNAME: {hostname}!!!")
