FROM python:3.8-slim-buster
RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list \
    && sed -i "s@http://security.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list \
    && cat /etc/apt/sources.list
RUN apt-get update \
    && apt-get install -y git libpq-dev libssl-dev gcc \
    && apt-get clean
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone
RUN mkdir /app
COPY . /app
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "/app:${PYTHONPATH}"
ENV CONFIG_PATH="/app/config.ini"
RUN python -m pip install --upgrade pip --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install -r requirements.txt --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 5000
CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]