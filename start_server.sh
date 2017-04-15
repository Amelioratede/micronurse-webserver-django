#!/usr/bin/env bash

tmux new-session -d -s MicroNurse-Web \
 "unset SSH_CLIENT;
  unset SSH_CONNECTION;
  unbuffer -p python3 ./manage.py runserver 0.0.0.0:13000 --noreload 2>&1 | tee -ai micronurse-webserver.log"
