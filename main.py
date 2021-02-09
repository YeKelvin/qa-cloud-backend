#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 2019/11/7 11:18
# @Author  : Kelvin.Ye
from server.app import create_app
# from server.extension import socketio
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    # socketio.run(app, debug=True, host='0.0.0.0', port=5000)
