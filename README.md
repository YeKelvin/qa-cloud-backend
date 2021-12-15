# QA CLOUD

## 安装依赖

```shell
pip install --upgrade poetry
cd qa-cloud-backend/
python3 -m poetry install
```

## 配置 click命令执行环境

### bash

```bash
set FLASK_APP=main.py;set FLASK_ENV=development;
```

### 虚拟环境添加pth

```shell
cd venv/Lib/site-packages
new file myproject.pth

# 将项目绝对路径添加至pth文件中
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

## MacOS安装uWSGI

MacOS下需要通过以下命令来安装，否则会报错，提示`OSError: unable to complete websocket handshake`

```bash
CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip install uwsgi -Iv
```

## 启动uWSGI

```bash
uwsgi --ini uwsgi.ini
```

## 启动Gunicorn
```bash
gunicorn -c gunicorn.conf main:app
```
