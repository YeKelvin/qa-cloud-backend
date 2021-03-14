#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script_execution_controller.py
# @Time    : 2021/2/9 10:41
# @Author  : Kelvin.Ye
from flask import request
from flask_socketio import emit
from server.common.utils.log_util import get_logger
from server.extension import socketio

log = get_logger(__name__)


@socketio.on('test_event')
def on_test_event(data):
    log.debug(f'socket sid:[ {request.sid} ] event:[ test_event ] received message:[ {data} ]')


@socketio.on('execution_result')
def execution_result(data):
    log.info(f'socket sid:[ {request.sid} ] event:[ execution_result ] received data:[ {data} ]')
    emit('execution_result', data, room=data['to'])


@socketio.on('execution_completed')
def execution_completed(data):
    log.info(f'socket sid:[ {request.sid} ] event:[ execution_completed ] received data:[ {data} ]')
    emit('execution_completed', None, room=data['to'])


@socketio.on('execution_log')
def execution_log(data):
    ...
