#!/usr/bin python3
# @File    : system_subscriber.py
# @Time    : 2023-04-21 16:48:07
# @Author  : Kelvin.Ye
# from loguru import logger
from flask import g

from app.extension import db
from app.modules.system.model import TSystemOperationLogContent
from app.signals import record_delete_signal
from app.signals import record_insert_signal
from app.signals import record_update_signal
from app.tools.identity import new_ulid
from app.tools.locals import threadlocal
from app.utils.json_util import to_json


@record_insert_signal.connect
def record_insert(sender, entity):
    """记录新增数据"""
    record = TSystemOperationLogContent()
    record.LOG_NO = get_traceid()
    record.OPERATION_TYPE = 'INSERT'
    record.TABLE_NAME = entity.__tablename__
    record.ROW_ID = entity.ID
    db.session.add(record)
    db.session.flush()


FILTERED_UPDATE_COLUMNS = [
    'ID', 'VERSION', 'DELETED', 'REMARK', 'CREATED_BY', 'CREATED_TIME', 'UPDATED_BY', 'UPDATED_TIME'
]


@record_update_signal.connect
def record_update(sender, entity, columnname, newvalue):
    """记录更新数据"""
    if columnname in FILTERED_UPDATE_COLUMNS:
        return
    oldvalue = getattr(entity, columnname, None)
    if oldvalue is None:
        return
    if isinstance(oldvalue, (dict, list)):
        oldvalue = to_json(oldvalue)
    if isinstance(newvalue, (dict, list)):
        newvalue = to_json(newvalue)
    record = TSystemOperationLogContent()
    record.LOG_NO = get_traceid(),
    record.OPERATION_TYPE = 'UPDATE',
    record.TABLE_NAME = entity.__tablename__,
    record.ROW_ID = entity.ID
    record.COLUMN_NAME = columnname,
    record.OLD_VALUE = oldvalue
    record.NEW_VALUE = newvalue
    db.session.add(record)
    db.session.flush()


@record_delete_signal.connect
def record_delete(sender, entity):
    """记录删除数据"""
    record = TSystemOperationLogContent()
    record.LOG_NO = get_traceid()
    record.OPERATION_TYPE = 'DELETE'
    record.TABLE_NAME = entity.__tablename__
    record.ROW_ID = entity.ID
    db.session.add(record)
    db.session.flush()


def get_traceid():
    if hasattr(g, 'trace_id'):
        return g.trace_id

    trace_id = getattr(threadlocal, 'trace_id', None)
    if not trace_id:
        trace_id = new_ulid()
        setattr(threadlocal, 'trace_id', trace_id)
    return trace_id
