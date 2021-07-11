#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database.py
# @Time    : 2019/11/7 10:57
# @Author  : Kelvin.Ye
from datetime import datetime

from app.extension import db
from app.utils.log_util import get_logger


log = get_logger(__name__)


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations"""

    @classmethod
    def insert(cls, **kwargs):
        entity = cls(**kwargs)
        entity.submit()

    @classmethod
    def query_by(cls, **kwargs):
        return cls.query.filter_by(DEL_STATE=0, **kwargs)

    @classmethod
    def select_first(cls, **kwargs):
        return cls.query_by(**kwargs).first()

    @classmethod
    def select_all(cls, **kwargs):
        return cls.query_by(**kwargs).all()

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


class BaseColumn:
    ID = db.Column(db.Integer, primary_key=True)
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
