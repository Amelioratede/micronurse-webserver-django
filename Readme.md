# micronurse-webserver-django

The web server of Micro Nurse IoT application. The version of Python used by this project is Python 3.

## Build and Start

① Install database MySQL and Redis, and start them.

② Install all needed Python modules via `pip3`:

```bash
pip3 install pillow django django-redis-cache djangorestframework hiredis mysqlclient paho-mqtt geopy
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

If the message resources (in `django.po`)  has been modified, the following command should be executed to compile updated message resources:

```shell
python3 ./manage.py migrate
```

## Sync Code to Remote Host

You can use `sync.sh` in root directory of project to sync your code to remote host. This script will sync your code via command  `rsync`.

Basic usage of `sync.sh`:

```shell
sync.sh ${REMOTE_HOST}
```

`$REMOTE_HOST` refer to address of remote host that you want to sync code to.

By default, remote user is `root`, and syncing path on remote host is `/root/micronurse-webserver`.

## Start Server at Backend

You can execute `start_server.sh`  in root directory of project directly to start server at backend.

## Relative Technical Documents

+ Django:[docs.djangoproject.com](https://docs.djangoproject.com) 
+ Django REST Framwork:[www.django-rest-framework.org](http://www.django-rest-framework.org) 