# micronurse-webserver-django

The web server of Micro Nurse IoT application. The version of Python used by this project is Python 3.

## Build and Start

① Install database MySQL and Redis, and start them.

② Install all needed Python modules via pip3:

```bash
pip3 install pillow django django-redis-cache djangorestframework hiredis mysqlclient paho-mqtt geopy
```

③ Init database as root user: 

Execute the following command in the root directory of project:

```bash
mysql -uroot -p -e "source init_db.sql"
```

④ Start server: 

Execute the following command in the root directory of project:

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

If the model has been modified, the following commands should be executed to apply the modification to the database:

```bash
python3 ./manage.py makemigrations micronurse_webserver
python3 ./manage.py migrate
```

### Message Resource Update

If the message resource(django.po) has been modified, the following command should be executed to compile the updated message resource:

```shell
python3 ./manage.py migrate
```

## Relative Technical Documents

+ Django:[docs.djangoproject.com](https://docs.djangoproject.com) 
+ Django REST Framwork:[www.django-rest-framework.org](http://www.django-rest-framework.org) 