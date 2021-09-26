#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database.py
# @Time    : 2019/11/7 10:57
# @Author  : Kelvin.Ye
import decimal
from sqlalchemy import func

from app.extension import db
from app.utils.log_util import get_logger
from app.utils.time_util import datetime_now_by_utc8


log = get_logger(__name__)


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations"""

    @classmethod
    def insert(cls, **kwargs):
        entity = cls(**kwargs)
        entity.submit()

    @classmethod
    def filter(cls, *args):
        return cls.query.filter(cls.DEL_STATE == 0, *args)

    @classmethod
    def filter_by(cls, **kwargs):
        return cls.query.filter_by(DEL_STATE=0, **kwargs)

    @classmethod
    def count_by(cls, **kwargs) -> int:
        return cls.query.session.query(func.count(cls.ID)).filter_by(DEL_STATE=0, **kwargs).scalar() or 0

    @classmethod
    def avg_by(cls, field, **kwargs) -> decimal.Decimal:
        return cls.query.session.query(func.avg(field)).filter_by(DEL_STATE=0, **kwargs).scalar() or 0

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            if value is not None:
                setattr(self, attr, value)
        self.submit()

    def delete(self):
        """软删除"""
        return self.update(DEL_STATE=1)

    def submit(self):
        """写入数据库但不提交"""
        db.session.add(self)
        db.session.flush()


class DBModel(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods"""

    __abstract__ = True

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class BaseColumnMixin:

    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='版本号')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
