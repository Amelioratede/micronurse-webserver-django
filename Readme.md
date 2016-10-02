# micronurse-webserver-django

## 配置与启动

①安装MySql、Redis、Python3

②安装必要的python模块：

```bash
pip3 install pillow django django-redis-cache djangorestframework hiredis mysqlclient paho-mqtt
```

③初始化数据库：以root用户身份运行init_db.sql

```bash
mysql -uroot -p -e "source init_db.sql"
```

④启动，在项目根目录下运行如下命令：

```bash
#如果是第一次运行或模型有更改就需要运行如下两个命令
python3 ./manage.py makemigrations micronurse_webserver
python3 ./manage.py migrate
#如果是第一次运行或消息字符串资源有更改就需要运行如下命令
python3 ./manage.py compilemessages
# 启动服务器于13000端口
python3 ./manage.py runserver 0.0.0.0:13000 --noreload
```

## 相关技术文档
+ Django:[docs.djangoproject.com](https://docs.djangoproject.com) 
+ Django REST Framwork:[www.django-rest-framework.org](http://www.django-rest-framework.org) 