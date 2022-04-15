#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : transaction.py
# @Time    : 2020/3/20 15:50
# @Author  : Kelvin.Ye
import inspect
from functools import wraps

from flask import request

from app.extension import db
from app.utils.log_util import get_logger


glog = get_logger(__name__)


def transactional(func):
    """DB事务装饰器"""
    log = getattr(inspect.getmodule(func), 'log', glog)

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            # 开始db事务，因为flask-sqlalchemy默认开启了事务，所以这里不用显示声明开始事务了
            # 调用service
            result = func(*args, **kwargs)
            # 提交db事务
            db.session.commit()
            return result
        except Exception:
            log.error(
                f'method:[ {request.method} ] path:[ {request.path} ] database session rollback'
            )
            db.session.rollback()
            raise  # 重新抛出异常给@http_service

    return wrapper
