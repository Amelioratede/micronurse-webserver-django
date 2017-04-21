# micronurse-webserver-django

The web server of Micro Nurse IoT application. The version of Python used by this project is Python 3.

## Build and Start

① Install database MySQL and Redis, and start them.

② Install all needed Python modules via `pip3`:

```bash
pip3 install pillow django django-redis-cache djangorestframework hiredis mysqlclient paho-mqtt geopy shortuuid
```

③ Init database as root user: 

Execute the following command in root directory of project:

```bash
mysql -uroot -p -e "source init_db.sql"
```

④ Add host name `micronurse-mqttbroker`, which refer to the host running [Micro Nurse MQTT Broker](https://github.com/micronurse-iot/micronurse-mqtt-broker-mosca), to `hosts` of your system. For example:

```
127.0.0.1	micronurse-mqttbroker
```

⑤ Start server: 

Execute the following command in root directory of project:

```bash
# Run the following three commands if first starting server.
python3 ./manage.py makemigrations micronurse_webserver
python3 ./manage.py migrate
python3 ./manage.py compilemessages
# Start server at port 13000
python3 ./manage.py runserver 0.0.0.0:13000 --noreload
```

##  Notice

### Model Modify

If the model has been modified, the following commands should be executed to apply modifications to database:

```bash
python3 ./manage.py makemigrations micronurse_webserver
python3 ./manage.py migrate
```

### Message Resource Update

Message resources of this project can be found in `micronurse_webserver/locale`.

If you have referred new message resources in Python code, you can execute following command to add new message resources to `django.po`:

```shell
python3 ./manage.py makemessages
```

If the message resources (in `django.po`)  has been modified, the following command should be executed to compile updated message resources:

```shell
python3 ./manage.py compilemessages
```

## Start Server at Backend

You can execute `start_server.sh`  to start server at port `13000` at backend directly.

And you can execute `tmux attach -t MicroNurse-Web` to view the log in real time.

## Sync Code to Remote Host

You can use `sync.sh` to sync your code to remote host. This script will sync your code via `rsync`.

Write into `sync_config.sh` as below to configure it.

```
remote_path=/root/micronurse-webserver
remote_user=root
remote_host=127.0.0.1
```

Lines in `sync_config.sh` will override the configuration set in `sync.sh`.

After that, you could sync your code.

## Relative Technical Documents

+ Django:[docs.djangoproject.com](https://docs.djangoproject.com) 
+ Django REST Framwork:[www.django-rest-framework.org](http://www.django-rest-framework.org) 