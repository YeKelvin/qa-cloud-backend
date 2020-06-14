# test-platform-server

## 安装依赖
python版本为3.7
```
pip install pipenv
cd test-platform-server/
pipenv install
```

## 配置 click命令行环境
```
set FLASK_APP=main.py
set FLASK_ENV=development
```
或PyCharm Settings->Tools->Terminal->Environment Variables添加如下变量
```
FLASK_APP=main.py;FLASK_ENV=development
```

## 初始化
```
flask initdb
flask initdata
```

## 调试
`flask run`
或
运行 main.py

## 服务端部署
Nginx, uWSGI, Supervisor

## 启动uWSGI
```
uwsgi --ini uWSGI.ini
```
