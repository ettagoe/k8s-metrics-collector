#!/bin/sh

touch /tmp/crontab.txt
echo "$CRON_SCHEDULE python /usr/src/app/src/agent/main.py 2>&1" >> /tmp/crontab.txt

/usr/bin/crontab /tmp/crontab.txt

# start cron
/usr/sbin/crond -f -l 8
