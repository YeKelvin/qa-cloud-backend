#!/usr/bin python3
# @File    : system_subscriber.py
# @Time    : 2023-04-21 16:48:07
# @Author  : Kelvin.Ye
# from loguru import logger
from flask import g
from loguru import logger

from app.extension import db
from app.modules.system.model import TRestApiLog
from app.modules.system.model import TSystemDataLog
from app.signals import record_delete_signal
from app.signals import record_insert_signal
from app.signals import record_update_signal
from app.signals import restapi_log_signal
from app.tools.cache import RULE_MAP
from app.tools.localvars import get_trace_id
from app.utils.json_util import to_json


# resrapi排除列表
URI_EXCLUDE = ['/execute']


@restapi_log_signal.connect
def record_restapi_log(sender, method, uri, request, response, success, elapsed):
    """记录restapi调用日志（POST、PUT、DELETE）"""
    try:
        # 仅记录POST、PUT或DELETE的请求
        if method not in ['POST', 'PUT', 'DELETE']:
            return
        # 过滤指定路径的请求
        for path in URI_EXCLUDE:
            if path in uri:
                return
        # 获取接口描述
        desc = RULE_MAP.get(f'{method} {uri}')
        if not desc:
            logger.warning(f'uri:[ {method} {uri} ] 缺失接口描述')
        # 记录日志
        record = TRestApiLog()
        record.LOG_NO=g.trace_id,
        record.DESC=desc
        record.IP=g.ip,
        record.URI=uri,
        record.METHOD=method,
        record.REQUEST=to_json(request),
        record.RESPONSE=to_json(response),
        record.SUCCESS=success
        record.ELAPSED_TIME=elapsed
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        logger.exception(str(e))


@record_insert_signal.connect
def record_insert(sender, entity):
    """记录新增数据"""
    record = TSystemDataLog()
    record.LOG_NO = get_trace_id()
    record.ACTION = 'INSERT'
    record.TABLE = entity.__tablename__
    record.ROWID = entity.ID
    db.session.add(record)
    db.session.flush()


# 数据更新排除列名
UPDATE_COLUMN_EXCLUDE = [
    'ID', 'VERSION', 'DELETED', 'REMARK', 'CREATED_BY', 'CREATED_TIME', 'UPDATED_BY', 'UPDATED_TIME'
]


@record_update_signal.connect
def record_update(sender, entity, columnname, newvalue):
    """记录更新数据"""
    if columnname in UPDATE_COLUMN_EXCLUDE:
        return
    oldvalue = getattr(entity, columnname, None)
    if oldvalue is None:
        return
    if isinstance(oldvalue, dict | list):
        oldvalue = to_json(oldvalue)
    if isinstance(newvalue, dict | list):
        newvalue = to_json(newvalue)
    record = TSystemDataLog()
    record.LOG_NO = get_trace_id(),
    record.ACTION = 'UPDATE',
    record.TABLE = entity.__tablename__,
    record.ROWID = entity.ID
    record.FIELD = columnname,
    record.OLD_VALUE = oldvalue
    record.NEW_VALUE = newvalue
    db.session.add(record)
    db.session.flush()


@record_delete_signal.connect
def record_delete(sender, entity):
    """记录删除数据"""
    record = TSystemDataLog()
    record.LOG_NO = get_trace_id()
    record.ACTION = 'DELETE'
    record.TABLE = entity.__tablename__
    record.ROWID = entity.ID
    db.session.add(record)
    db.session.flush()
