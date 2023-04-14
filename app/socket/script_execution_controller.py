#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : script_execution_controller.py
# @Time    : 2021/2/9 10:41
# @Author  : Kelvin.Ye
from flask import request
from flask_socketio import emit
from loguru import logger

from app.extension import socketio


@socketio.on('test_event')
def on_test_event(data):
    logger.debug(f'socket sid:[ {request.sid} ] event:[ test_event ] received message:[ {data} ]')


@socketio.on('execution_result')
def execution_result(data):
    logger.info(f'socket sid:[ {request.sid} ] event:[ execution_result ] received data:[ {data} ]')
    emit('execution_result', data, room=data['to'])


@socketio.on('execution_completed')
def execution_completed(data):
    logger.info(f'socket sid:[ {request.sid} ] event:[ execution_completed ] received data:[ {data} ]')
    emit('execution_completed', None, room=data['to'])


@socketio.on('execution_log')
def execution_log(data):
    ...
