#!/usr/bin/ python3
# @File    : pubilc_controller.py
# @Time    : 2021/2/9 10:41
# @Author  : Kelvin.Ye
from flask import request
from loguru import logger

from app.extension import socketio


@socketio.on('connect')
def handle_connect():
    logger.info(
        f'socketid:[ {request.sid} ] '
        f'event:[ {request.event["message"]} ] '
        f'namespace:[ {request.namespace} ] '
        f'uri:[ {request.method}] {request.path} ] '
        f'header:[ {dict(request.headers)} ] '
        f'request:[ {request.values.to_dict()} ]'
    )
    # TODO： 登录校验


@socketio.on('disconnect')
def handle_disconnect():
    logger.info(
        f'socketid:[ {request.sid} ] '
        f'event:[ {request.event["message"]} ] '
        f'namespace:[ {request.namespace} ] '
        f'uri:[ {request.method}] {request.path} ] '
        f'header:[ {dict(request.headers)} ] '
        f'request:[ {request.values.to_dict()} ]'
    )


@socketio.on_error_default
def handle_error_default(e):
    """Handles all namespaces"""
    logger.exception(
        f'socketid:[ {request.sid} ] '
        f'event:[ {request.event["message"]} ] '
        f'namespace:[ {request.namespace} ] '
        f'uri:[ {request.method}] {request.path} ] '
        f'header:[ {dict(request.headers)} ] '
        f'request:[ {request.values.to_dict()} ]\n'
        f'{e}'
    )
