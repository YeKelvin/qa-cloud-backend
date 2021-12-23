# QA CLOUD BACKEND

## 安装依赖

```bash
cd qa-cloud-backend/
poetry install
```

### 虚拟环境添加pth

```bash
cd venv/Lib/site-packages
touch myproject.pth

# 将项目绝对路径添加至pth文件中
```

## 初始化数据库

```bash
flask initdb
flask initdata
```

## 开发环境调试

```bash
flask run
```

## 生产部署

Nginx, uWSGI, Docker

### 创建容器网络

```bash
docker network create main
```


### Docker构建

```bash
docker build -t qa-cloud-backend .
```

**需要翻墙的话额外添加`build-arg`参数**
```bash
--build-arg HTTP_PROXY=http://docker.for.mac.host.internal:1087 --build-arg HTTPS_PROXY=http://docker.for.mac.host.internal:1087
--build-arg HTTP_PROXY=http://host.docker.internal:10809 --build-arg HTTPS_PROXY=http://host.docker.internal:10809
```

### Docker运行

```bash
docker run -d --network main -p 5000:5000 --name svc-qa-cloud-service qa-cloud-backend
```
