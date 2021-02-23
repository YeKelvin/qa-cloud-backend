#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script_execution_controller.py
# @Time    : 2021/2/9 10:41
# @Author  : Kelvin.Ye
from typing import Final

from flask_socketio import emit, send
from server.common.utils.log_util import get_logger
from server.extension import socketio

log = get_logger(__name__)

NAMESPACE = '/script'  # type:Final


@socketio.on('test_event')
def on_test_event(data):
    log.debug(f'event:[ test_event ] received message:[ {data} ]')


@socketio.on('execution_log', namespace=NAMESPACE)
def execution_log(data):
    ...


@socketio.on_error('/log')
def error_handler_log(e):
    ...
