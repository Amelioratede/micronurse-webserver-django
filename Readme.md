# micronurse-webserver-django


## 配置与启动

①安装Sqlite3、Redis、Python3

②安装必要的python模块：

```bash
sudo pip install pillow django django-redis-cache django-redis-sessions
```

③启动，在项目根目录下运行如下命令：

```bash
#如果是第一次运行或模型有更改就需要运行如下两个命令
python3 ./manage.py makemigrations
python3 ./manage.py migrate
# 启动服务器于13000端口
python3 ./manage.py runserver 0.0.0.0:13000
```
