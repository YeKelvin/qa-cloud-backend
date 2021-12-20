FROM python:3.8-slim-buster
RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list \
    && apt-get update \
    && apt-get install --no-install-recommends -y gcc git build-essential libpq-dev libssl-dev python-dev\
    && apt-get clean \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone
WORKDIR /app
COPY . /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "/app:${PYTHONPATH}"
ENV CONFIG_PATH "/app/config.ini"
RUN python -m pip install --upgrade pip --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install -r requirements.txt --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple
# RUN CFLAGS="-I/usr/local/include/python3.8" UWSGI_PROFILE="asyncio" pip install uwsgi --no-binary :all: --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install uwsgi -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 5000
CMD ["uwsgi", "--ini", "uwsgi.ini"]