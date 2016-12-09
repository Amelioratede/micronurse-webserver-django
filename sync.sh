#!/bin/bash

function show_help(){
    echo "Usage: sync.sh <remote_host_address> [remote_path] [remote_user]"
}

remote_path=/root/micronurse-webserver
remote_user=root

if [ $# -gt 0 ]; then
    if [ $1 == "--help" ]; then
        show_help
        exit 0
	elif [ $# -gt 1 ]; then
	    remote_path=$2
	    if [ $# -gt 2 ]; then
	        remote_user=$3
	    fi
	fi
else
	show_help
	exit 1
fi

rsync --recursive --copy-links --perms --times --delete --progress --human-readable --exclude=db.sqlite3 --exclude=micronurse_webserver/migrations/ --exclude=__pycache__ --exclude=.DS_Store * ${remote_user}@$1:${remote_path}

