#!/bin/bash

remote_path=/root/micronurse-webserver
remote_user=root
remote_host=127.0.0.1

if [ -f sync_config.sh ]; then
    source sync_config.sh;
fi

rsync --recursive --copy-links --perms --times --delete --progress --human-readable --exclude=db.sqlite3 --exclude=migrations --exclude=__pycache__ --exclude=.DS_Store --exclude=*.log * "${remote_user}@${remote_host}:${remote_path}"
