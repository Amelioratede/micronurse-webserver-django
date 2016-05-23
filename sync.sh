#!/bin/bash

rsync --recursive --copy-links --perms --times --delete --progress --human-readable --exclude=db.sqlite3 --exclude=micronurse_webserver/migrations/ --exclude=__pycache__ --exclude=.DS_Store * root@101.200.144.204:~/micronurse-webserver

