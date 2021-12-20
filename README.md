# QA CLOUD

## 安装依赖

```bash
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

```bash
cd venv/Lib/site-packages
touch myproject.pth

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

Nginx, uWSGI, Docker

## MacOS安装uWSGI

MacOS下需要通过以下命令来安装，否则会报错，提示`OSError: unable to complete websocket handshake`

```bash
CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip install uwsgi -Iv
```

## 启动uWSGI

```bash
uwsgi --ini uwsgi.ini
```
## Docker构建
#### MacOS

```bash
docker build -t qa-cloud-backend . --build-arg HTTP_PROXY=http://docker.for.mac.host.internal:1087 --build-arg HTTPS_PROXY=http://docker.for.mac.host.internal:1087
```

#### Windows

```bash
docker build -t qa-cloud-backend . --build-arg HTTP_PROXY=http://host.docker.internal:10809 --build-arg HTTPS_PROXY=http://host.docker.internal:10809
```

## 生产运行
```bash
docker run -d --network main -p 5000:5000 --name uwsgi.app qa-cloud-backend
```

## 创建容器网络

```bash
docker network create main
```
