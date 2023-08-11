#!/usr/bin python3
# @File    : io.py
# @Time    : 2023-08-08 15:23:36
# @Author  : Kelvin.Ye
from flask import request
from loguru import logger

from app.extension import socketio


def emit(event, *args, **kwargs):
    data = args[0] if args else kwargs.get('data')
    sid = kwargs.get('to', request.sid)
    ns = kwargs.get('namespace', '/')
    logger.info(f'namespace:[ {ns} ] socketid:[ {sid} ] event:[ {event} ] emit:[ {data} ]')
    socketio.emit(event, data, to=sid, namespace=ns)
