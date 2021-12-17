FROM python:3.8-slim-buster
RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list \
    && sed -i "s@http://security.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list \
    && cat /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y git libpq-dev gcc \
    && apt-get clean \
    && git config --global http.proxy http://host.docker.internal:10809 \
    && python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN mkdir /app
WORKDIR /app
COPY . /app
ENV CONFIG_PATH /app/config.ini
#RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN poetry run uwsgi --ini uwsgi.ini
