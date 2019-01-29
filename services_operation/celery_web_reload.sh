#!/usr/bin/env bash
OCTO_PATH="/var/www/web_app_dir"
OCTO_BIN="/app/bin"
LOG="/var/log/appdir/RESTART.log"
touch ${LOG}
chmod +w ${LOG}
echo "-=== Start reloading: `date` ==-" >> ${LOG}
echo "0. The log is here ${LOG}"


echo "0. Reload & restart Apache, Celery workers\Beat, Flower"| tee -a ${LOG}
ACTIVE="Active: active (running)"

if [[ `systemctl status httpd.service  | grep "${ACTIVE}"` ]]; then
    echo "4. Reloading Apache service!" | tee -a ${LOG}
    systemctl reload httpd.service  2>&1 | tee -a ${LOG}
else
    echo "4. WARNING: Apache is not running!!" | tee -a ${LOG}
fi

if [[ `systemctl status celery.service | grep "${ACTIVE}"` ]]; then
    echo "3. Restarting celery service!" | tee -a ${LOG}
    systemctl restart celery.service  2>&1 | tee -a ${LOG}
else
    echo "3. WARNING: Celery is not running!!" | tee -a ${LOG}
fi

if [[ `systemctl status celerybeat.service  | grep "Active: active"` ]]; then
    echo "2. Restarting celerybeat service!" | tee -a ${LOG}
    systemctl restart celerybeat.service  2>&1 | tee -a ${LOG}
else
    echo "2. WARNING: Celerybeat is not running!!"| tee -a ${LOG}
fi

if [[ `systemctl status flower.service  | grep "${ACTIVE}"` ]]; then
    echo "1. Restarting flower service!" | tee -a ${LOG}
    systemctl restart flower.service  2>&1 | tee -a ${LOG}
else
    echo "1. WARNING: Flower is not running!!" | tee -a ${LOG}
fi


# Now ping celery
echo "0. Ping CELERY workers to activate sync" | tee -a ${LOG}
. ${OCTO_PATH}${OCTO_BIN}/activate
cd ${OCTO_PATH}
celery -A octo inspect ping >> ${LOG} 2>&1
deactivate

echo "0. Reload & restart finished!"| tee -a ${LOG}
echo "-== Finish reloading: `date` ==-" >> ${LOG}
