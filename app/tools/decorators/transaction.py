#!/usr/bin/ python3
# @File    : transaction.py
# @Time    : 2020/3/20 15:50
# @Author  : Kelvin.Ye
from functools import wraps

from flask import g
from flask import request
from loguru import logger

from app.extension import db
from app.tools.exceptions import ServiceError


# TODO: 干掉
def transactional(func):
    """DB事务装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # 开始db事务，因为flask-sqlalchemy默认开启了事务，所以这里不用显示声明开始事务了
            # 调用service
            result = func(*args, **kwargs)
            # 提交db事务
            db.session.commit()
            return result
        except ServiceError:
            db.session.rollback()
            logger.bind(traceid=g.trace_id).info(f'uri:[ {request.method} {request.path} ] 数据回滚')
            raise  # 重新抛出异常给@http_service
        except Exception:
            db.session.rollback()
            logger.bind(traceid=g.trace_id).error(f'uri:[ {request.method} {request.path} ] 数据回滚')
            raise  # 重新抛出异常给@http_service

    return wrapper
