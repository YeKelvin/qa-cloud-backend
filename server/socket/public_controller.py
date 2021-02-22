#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : pubilc_controller.py
# @Time    : 2021/2/9 10:41
# @Author  : Kelvin.Ye
from server.common.utils.log_util import get_logger
from server.extension import socketio
from flask import request

log = get_logger(__name__)


@socketio.on('connect')
def on_connect():
    log.info(f'socket event:[ connect ] sid:[ {request.sid} ]')
    log.debug(f'socket request:[ {request.__dict__} ]')


@socketio.on('reconnect')
def on_reconnect():
    log.info(f'socket event:[ reconnect ] sid:[ {request.sid} ]')
    log.debug(f'socket request:[ {request.__dict__} ]')


@socketio.on('disconnect')
def on_disconnect():
    log.info(f'socket event:[ disconnect ] sid:[ {request.sid} ]')
    log.debug(f'socket request:[ {request.__dict__} ]')


@socketio.on('message')
def on_message(data):
    log.info(f'socket event:[ message ] sid:[ {request.sid} ] received message:[ {data} ]')
    log.debug(f'socket request:[ {request.__dict__} ]')


@socketio.on_error_default
def error_handler(e):
    ...
