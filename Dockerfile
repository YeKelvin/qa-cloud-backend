FROM python:3.8-slim-buster
RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list \
    && apt-get update \
    && apt-get install --no-install-recommends -y build-essential gcc git libpq-dev libssl-dev \
    && apt-get clean \
    && rm -rf /tmp/* \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone
WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install -r requirements.txt --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV APP_CONFIG_FILE=/app/config.ini
EXPOSE 5000
CMD ["uwsgi", "--ini", "uwsgi.ini"]