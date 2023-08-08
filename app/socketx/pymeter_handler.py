#!/usr/bin python3
# @File    : pymeter_handler.py
# @Time    : 2023-08-04 16:20:09
# @Author  : Kelvin.Ye
from flask import request

from app.extension import socketio
from app.socketx.io import emit
from app.tools.cache import EXECUTING_PYMETER_STORE
from app.tools.service import socket_service


@socketio.on('pymeter:cancel_execution')
@socket_service
def cancel_execution():
    """用户中断调试"""
    socket_id = request.sid
    if socket_id not in EXECUTING_PYMETER_STORE:
        return
    running = get_running_pymeter(socket_id)
    stop_event = running.get('stop_event')
    stop_event.set()
    emit(
        'pymeter:user_interrupted',
        data={'resultId': running.get('result_id'), 'result': {'loading': False, 'running': False}},
        to=socket_id,
        namespace='/'
    )


def get_running_pymeter(socket_id):
    return EXECUTING_PYMETER_STORE[socket_id]
