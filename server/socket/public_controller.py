#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : pubilc_controller.py
# @Time    : 2021/2/9 10:41
# @Author  : Kelvin.Ye
import traceback

from flask import request
from server.utils.log_util import get_logger
from server.extension import socketio

log = get_logger(__name__)


@socketio.on('connect')
def handle_connect():
    log.info(
        f'socket sid:[ {request.sid} ] event:[ {request.event["message"]} ] namespace:[ {request.namespace} ] '
        f'method:[{request.method}] path:[ {request.path} ] request:[ {request.values.to_dict()} ]'
    )


@socketio.on('connect_error')
def handle_connect_error():
    log.error(
        f'socket sid:[ {request.sid} ] event:[ {request.event["message"]} ] namespace:[ {request.namespace} ] '
        f'method:[{request.method}] path:[ {request.path} ] request:[ {request.values.to_dict()} ]'
    )


@socketio.on('reconnect')
def handle_reconnect():
    log.info(
        f'socket sid:[ {request.sid} ] event:[ {request.event["message"]} ] namespace:[ {request.namespace} ] '
        f'method:[{request.method}] path:[ {request.path} ] request:[ {request.values.to_dict()} ]'
    )


@socketio.on('disconnect')
def handle_disconnect():
    log.info(
        f'socket sid:[ {request.sid} ] event:[ {request.event["message"]} ] namespace:[ {request.namespace} ] '
        f'method:[{request.method}] path:[ {request.path} ] request:[ {request.values.to_dict()} ]'
    )


@socketio.on_error_default
def handle_error_default(e):
    log.error(
        f'socket sid:[ {request.sid} ] event:[ {request.event["message"]} ] namespace:[ {request.namespace} ] '
        f'method:[{request.method}] path:[ {request.path} ] request:[ {request.values.to_dict()} ] '
        f'\n{traceback.format_exc()}')


# @socketio.on_error()
# def handle_erro(e):
#     """Handles the default namespace"""
#     ...
