FROM python:3.8-slim-buster
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip install poetry -i https://mirrors.aliyun.com/pypi/simple/
RUN poetry install
ENV CONFIG_PATH /app/config.ini
RUN uwsgi --ini uwsgi.ini
EXPOSE 5000
