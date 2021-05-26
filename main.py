#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 2019/11/7 11:18
# @Author  : Kelvin.Ye
from gevent.pywsgi import WSGIServer

from app import create_app
from app.utils.log_util import get_logger

log = get_logger(__name__)
app = create_app()


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=5000)
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
