# test-platform-server

## 安装依赖

```shell
pip install --upgrade poetry
cd test-platform-server/
python3 -m poetry install
```

## 安装send-anywhere模块

```bash
pip3 install git+https://github.com/YeKelvin/send-anywhere.git
cd send-anywhere/
python3 setup.py build
python3 setup.py sdist
cd dist/
tar -zxvf send-anywhere-{version}.tar.gz
cd send-anywhere-{version}/
python3 setup.py install
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

Nginx, uWSGI, Supervisor

## 启动uWSGI

```bash
uwsgi --ini uwsgi.ini
```

## 监控面板
```url
/dashboard
```

## 技术说明

站在巨人的肩上，离不开开源的支持，主要使用到的技术如下：
...
