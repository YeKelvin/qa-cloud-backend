#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : transaction
# @Time    : 2020/3/20 15:50
# @Author  : Kelvin.Ye
import traceback
from functools import wraps

from flask import request, g

from server.extensions import db
from server.utils.log_util import get_logger

log = get_logger(__name__)


def db_transaction(func):
    """DB事务装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
            db.session.commit()
        except Exception:
            log.error(
                f'logId:[ {g.logid} ] method:[ {request.method} ] path:[ {request.path} ] '
                f'traceback:[ {traceback.format_exc()} ]'
            )
            db.session.rollback()
            raise  # 重新抛出给 @http_service
        finally:
            return result

    return wrapper
