#!/usr/bin python3
# @File    : data_service.py
# @Time    : 2023-09-25 14:29:57
# @Author  : Kelvin.Ye
from sqlalchemy import select

from app.database import db_scalars
from app.modules.system.model import TSystemDataChangelog
from app.tools.service import http_service


@http_service
def query_data_log(req):
    changelogs = db_scalars(
        select(TSystemDataChangelog)
        .where(
            TSystemDataChangelog.exclude_deleted_data(),
            TSystemDataChangelog.LOG_NO == req.logNo
        )
    ).all()

    return [
        {
            'logNo': log.LOG_NO,
            'action': log.ACTION,
            'table': log.TABLE,
            'rowid': log.ROWID,
            'field': log.FIELD,
            'oldValue': log.OLD_VALUE,
            'newValue': log.NEW_VALUE
        }
        for log in changelogs
    ]


@http_service
def query_data_trace(req):
    ...


@http_service
def query_data_log_list(req):
    ...
