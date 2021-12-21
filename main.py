#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 2019/11/7 11:18
# @Author  : Kelvin.Ye
from app import create_app


app = create_app()


if __name__ == '__main__':
    # from werkzeug.debug import DebuggedApplication
    # app = DebuggedApplication(app, evalex=True)
    from gevent.pywsgi import WSGIServer
    server = WSGIServer(('', 5000), app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.stop()
