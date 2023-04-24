#!/usr/bin python3
# @File    : openapi_subscriber.py
# @Time    : 2023-04-21 18:25:08
# @Author  : Kelvin.Ye
from flask import g

from app.extension import db
from app.modules.opencenter.model import TOpenApiLog
from app.signals import openapi_log_signal
from app.utils.json_util import to_json


@openapi_log_signal.connect
def record_openapi_log(sender, method, uri, request, response, success, elapsed):
    """记录openapi调用日志（POST、PUT、DELETE）"""
    record = TOpenApiLog()
    record.LOG_NO=g.trace_id,
    record.APP_NO=g.thirdparty_app_no,
    record.IP=g.ip,
    record.URI=uri,
    record.METHOD=method,
    record.REQUEST=to_json(request),
    record.RESPONSE=to_json(response),
    record.SUCCESS=success
    record.ELAPSED_TIME=elapsed
    db.session.add(record)
    db.session.flush()
