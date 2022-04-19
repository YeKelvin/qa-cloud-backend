#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database.py
# @Time    : 2019/11/7 10:57
# @Author  : Kelvin.Ye
import decimal
from typing import Type

from flask import g
from sqlalchemy import func

from app.common.globals import get_userno
from app.extension import db
from app.utils.log_util import get_logger
from app.utils.time_util import datetime_now_by_utc8


log = get_logger(__name__)


MODEL = Type[db.Model]


class setter(dict):  # noqa
    ...


class where(list):  # noqa
    ...


class where_by(dict):  # noqa
    ...


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations"""

    @classmethod
    def insert(cls: MODEL, **kwargs):
        # record = kwargs.pop('record', True)
        entity = cls(**kwargs)
        entity.submit()
        # record and __record_insert__(entity)

    @classmethod
    def filter(cls: MODEL, *args):
        return cls.query.filter(cls.DELETED == 0, *args)

    @classmethod
    def filter_by(cls: MODEL, **kwargs):
        return cls.query.filter_by(DELETED=0, **kwargs)

    @classmethod
    def count_by(cls: MODEL, **kwargs) -> int:
        return cls.query.session.query(func.count(cls.ID)).filter_by(DELETED=0, **kwargs).scalar() or 0

    @classmethod
    def avg_by(cls: MODEL, field, **kwargs) -> decimal.Decimal:
        return cls.query.session.query(func.avg(field)).filter_by(DELETED=0, **kwargs).scalar() or 0

    @classmethod
    def updates(cls: MODEL, setter: dict, args: list, record=True):
        """e.g.: Table.updates(setter(), where())"""
        cls.filter(*args).update({getattr(cls, attr): value for attr, value in setter.items()})
        db.session.flush()

    @classmethod
    def updates_by(cls: MODEL, setter: dict, kwargs: dict, record=True):
        """e.g.: Table.updates(setter(), where_by())"""
        cls.filter_by(**kwargs).update({getattr(cls, attr): value for attr, value in setter.items()})
        # entities = cls.filter_by(**kwargs).all()
        # for attr, value in setter.items():
        #   for entity in entities:
        #     setattr(self, attr, value)
        #     __record_update__(getattr(cls, '__tablename__'), getattr(entity, attr), value)
        db.session.flush()

    @classmethod
    def deletes(cls: MODEL, *args, record=True):
        cls.filter(*args).update({cls.DELETED: cls.ID})
        db.session.flush()

    @classmethod
    def deletes_by(cls: MODEL, **kwargs):
        # record = kwargs.pop('record', True)
        cls.filter_by(**kwargs).update({cls.DELETED: cls.ID})
        # entities = cls.filter_by(**kwargs).all()
        # for entity in entities:
        #     entity.DELETED = entity.ID
        #     __record_delete__(entity)
        db.session.flush()

    def update(self: MODEL, **kwargs):
        # record = kwargs.pop('record', True)
        for attr, value in kwargs.items():
            setattr(self, attr, value)
            # record and __record_update__(getattr(self, '__tablename__'), getattr(self, attr), value)
        self.submit()

    def delete(self: MODEL, record=True):
        """软删除"""
        self.update(DELETED=getattr(self, 'ID'))
        # record and __record_delete__(self)

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
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='版本号')
    DELETED = db.Column(db.Integer, nullable=False, default=0, comment='是否为已删除的数据')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), default=get_userno, comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), default=get_userno, onupdate=get_userno, comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TSystemOperationLogContent(DBModel, BaseColumn):
    """操作日志内容表"""
    __tablename__ = 'SYSTEM_OPERATION_LOG_CONTENT'
    LOG_NO = db.Column(db.String(32), index=True, nullable=False, comment='日志编号')
    OPERATION_TYPE = db.Column(db.String(32), nullable=False, comment='操作类型(INSERT:新增, UPDATE:修改, DELETE:删除)')
    TABLE_NAME = db.Column(db.String(128), comment='列名')
    ROW_ID = db.Column(db.Integer, comment='新增行或删除行的ID')
    COLUMN_NAME = db.Column(db.String(128), comment='列名')
    OLD_VALUE = db.Column(db.Text, comment='旧值')
    NEW_VALUE = db.Column(db.Text, comment='新值')


def __record_insert__(entity):
    content = TSystemOperationLogContent()
    content.LOG_NO = g.trace_id,
    content.OPERATION_TYPE = 'INSERT',
    content.TABLE_NAME = entity.__tablename__,
    content.ROW_ID = entity.ID
    db.session.add(content)
    db.session.flush()


def __record_update__(tablename, old, new):
    content = TSystemOperationLogContent()
    content.LOG_NO = g.trace_id,
    content.OPERATION_TYPE = 'UPDATE',
    content.TABLE_NAME = tablename,
    content.OLD_VALUE = old
    content.NEW_VALUE = new
    db.session.add(content)
    db.session.flush()


def __record_delete__(entity):
    content = TSystemOperationLogContent()
    content.LOG_NO = g.trace_id,
    content.OPERATION_TYPE = 'DELETE',
    content.TABLE_NAME = entity.__tablename__,
    content.ROW_ID = entity.ID
    db.session.add(content)
    db.session.flush()
