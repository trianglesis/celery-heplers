#!/usr/bin/env bash
OCTO_PATH="/var/www/app_dir"
OCTO_BIN="/app/bin"
LOG="/var/log/app_dir/RESTART.log"
touch ${LOG}
chmod +w ${LOG}
echo "-=== Start restarting: `date` ==-" >> ${LOG}
echo "0. The log is here ${LOG}"


echo "0. Restarting RabbitMQ, Apache, Celery workers\Beat, Flower, Mysql"
ACTIVE="Active: active (running)"

if [[ `systemctl status rabbitmq-server | grep "${ACTIVE}"` ]]; then
    echo "6. Restarting rabbitmq-server!" | tee -a ${LOG}
    systemctl restart rabbitmq-server 2>&1 | tee -a ${LOG}
else
    echo "6. Rabbitmq-server is not running!!" | tee -a ${LOG}
fi

if [[ `systemctl status httpd.service  | grep "${ACTIVE}"` ]]; then
    echo "5. Restarting Apache service!" | tee -a ${LOG}
    systemctl restart httpd.service 2>&1 | tee -a ${LOG}
else
    echo "5. Apache is not running!!" | tee -a ${LOG}
fi

if [[ `systemctl status celery.service  | grep "${ACTIVE}"` ]]; then
    echo "4. Restarting celery service!" | tee -a ${LOG}
    systemctl restart celery.service 2>&1 | tee -a ${LOG}
else
    echo "4. Celery is not running!!" | tee -a ${LOG}
fi

if [[ `systemctl status celerybeat.service  | grep "Active: active"` ]]; then
    echo "3. Restarting celerybeat service!" | tee -a ${LOG}
    systemctl restart celerybeat.service 2>&1 | tee -a ${LOG}
else
    echo "3. Celerybeat is not running!!" | tee -a ${LOG}
fi

if [[ `systemctl status flower.service  | grep "${ACTIVE}"` ]]; then
    echo "2. Restarting flower service!" | tee -a ${LOG}
    systemctl restart flower.service 2>&1 | tee -a ${LOG}
else
    echo "2. Flower is not running!!" | tee -a ${LOG}
fi

if [[ `systemctl status mysqld | grep "${ACTIVE}"` ]]; then
    echo "1. Restarting mysqld!" | tee -a ${LOG}
    systemctl restart mysqld 2>&1 | tee -a ${LOG}
else
    echo "1. Mysql server is not running!!" | tee -a ${LOG}
fi

# Now ping celery
echo "0. Ping CELERY workers to activate sync" | tee -a ${LOG}
. ${OCTO_PATH}${OCTO_BIN}/activate
cd ${OCTO_PATH}
celery -A octo inspect ping >> ${LOG} 2>&1
deactivate

echo "0. Restart finished!"| tee -a ${LOG}
echo "-== Finish restarting: `date` ==-" >> ${LOG}
