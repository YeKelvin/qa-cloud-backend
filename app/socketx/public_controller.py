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
        f'socket sid:[ {request.sid} ] event:[ {request.event["message"]} ] namespace:[ {request.namespace} ] '
        f'method:[{request.method}] path:[ {request.path} ] request:[ {request.values.to_dict()} ]'
    )


@socketio.on('connect_error')
def handle_connect_error():
    logger.error(
        f'socket sid:[ {request.sid} ] event:[ {request.event["message"]} ] namespace:[ {request.namespace} ] '
        f'method:[{request.method}] path:[ {request.path} ] request:[ {request.values.to_dict()} ]'
    )


@socketio.on('reconnect')
def handle_reconnect():
    logger.info(
        f'socket sid:[ {request.sid} ] event:[ {request.event["message"]} ] namespace:[ {request.namespace} ] '
        f'method:[{request.method}] path:[ {request.path} ] request:[ {request.values.to_dict()} ]'
    )


@socketio.on('disconnect')
def handle_disconnect():
    logger.info(
        f'socket sid:[ {request.sid} ] event:[ {request.event["message"]} ] namespace:[ {request.namespace} ] '
        f'method:[{request.method}] path:[ {request.path} ] request:[ {request.values.to_dict()} ]'
    )


@socketio.on_error_default
def handle_error_default(e):
    logger.exception(
        f'socket sid:[ {request.sid} ] event:[ {request.event["message"]} ] namespace:[ {request.namespace} ] '
        f'method:[{request.method}] path:[ {request.path} ] request:[ {request.values.to_dict()} ] '
    )


# @socketio.on_error()
# def handle_erro(e):
#     """Handles the default namespace"""
#     ...
