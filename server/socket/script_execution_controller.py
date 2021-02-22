#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script_execution_controller.py
# @Time    : 2021/2/9 10:41
# @Author  : Kelvin.Ye
from flask_socketio import emit
from server.common.utils.log_util import get_logger
from server.extension import socketio

log = get_logger(__name__)


@socketio.on('test')
def on_test(data):
    emit('received')
    log.info(f'i am test event, received data={data}')
