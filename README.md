# test-platform-server

## 安装依赖

```shell
pip install --upgrade poetry
cd test-platform-server/
python3 -m poetry install
```

## 配置 click命令执行环境

### bash

```bash
set FLASK_APP=main.py;set FLASK_ENV=development
```

### 虚拟环境添加pth

```shell
cd venv/Lib/site-packages
new file myproject.pth
添加项目绝对路径
```

## 初始化

```bash
flask initdb
flask initdata
```

## 调试

`flask run --host 0.0.0.0 --port 5000`
或
运行 main.py

## 服务端部署

Nginx, uWSGI, Systemd / Supervisor

## 启动uWSGI

```bash
uwsgi --ini uwsgi.ini
```

## 配置Nginx
```conf
server {
    listen XXXX default_server;#指定监听的端口
    charset utf-8;

    server_name XX.XXX.XXX.XXX; # ip地址

    location /recognize {
        include      uwsgi_params;
        uwsgi_pass   127.0.0.1:8081;
        uwsgi_param  UWSGI_PYHOME /path/to/venv;
        uwsgi_param  UWSGI_CHDIR /path/to/project;
        uwsgi_param  UWSGI_SCRIPT flask_web:application;
        uwsgi_read_timeout 300;
        uwsgi_connect_timeout 300;
        uwsgi_send_timeout 300;
    }
}
# 配置uwsgi时，UWSGI_CHDIR和UWSGI_SCRIPT这两条命令顺序敏感，如果脚本在目录上一行也会导致服务无法启动。
```

## 监控面板

```url
/dashboard
```

## 技术说明

站在巨人的肩上，主要使用了以下开源项目：
...
