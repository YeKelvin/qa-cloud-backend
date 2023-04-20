#!/usr/bin/ python3
# @File    : database.py
# @Time    : 2019/11/7 10:57
# @Author  : Kelvin.Ye
import decimal
from typing import Type

from flask import g
from sqlalchemy import func

from app.extension import db
from app.tools.identity import new_ulid
from app.tools.locals import threadlocal
from app.tools.localvars import get_userno_or_default
from app.utils.json_util import to_json
from app.utils.time_util import datetime_now_by_utc8


MODEL = Type[db.Model]


def dbquery(*args, **kwargs):
    return db.session.query(*args, **kwargs)


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
        record = kwargs.pop('record', True)
        entity = cls(**kwargs)
        entity.submit()
        record and record_insert(entity)

    @classmethod
    def insert_without_record(cls: MODEL, **kwargs):
        kwargs['record'] = False
        cls.insert(**kwargs)

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
    def sum_by(cls: MODEL, field, cons: dict) -> decimal.Decimal:
        """e.g.:

        from app.database import where_by

        Table.sum_by(setter(), where_by())
        """
        return cls.query.session.query(func.sum(field)).filter_by(DELETED=0, **cons).scalar() or 0

    @classmethod
    def avg_by(cls: MODEL, field, **kwargs) -> decimal.Decimal:
        return cls.query.session.query(func.avg(field)).filter_by(DELETED=0, **kwargs).scalar() or 0

    @classmethod
    def updates(cls: MODEL, setter: dict, cons: list, record=True):
        """e.g.:

        from app.database import setter
        from app.database import where

        Table.updates(setter(), where())
        """
        if record:
            entities = cls.filter(*cons).all()
            for entity in entities:
                entity.update(**setter)
        else:
            cls.filter(*cons).update({getattr(cls, attr): value for attr, value in setter.items()})
        db.session.flush()

    @classmethod
    def updates_by(cls: MODEL, setter: dict, cons: dict, record=True):
        """e.g.:

        from app.database import setter
        from app.database import where_by

        Table.updates(setter(), where_by())
        """
        if record:
            entities = cls.filter_by(**cons).all()
            for entity in entities:
                entity.update(**setter)
        else:
            cls.filter_by(**cons).update({getattr(cls, attr): value for attr, value in setter.items()})
        db.session.flush()

    @classmethod
    def deletes(cls: MODEL, *args, record=True):
        if record:
            entities = cls.filter(*args).all()
            for entity in entities:
                entity.delete()
        else:
            cls.filter(*args).update({cls.DELETED: cls.ID})
        db.session.flush()

    @classmethod
    def deletes_by(cls: MODEL, **kwargs):
        if kwargs.pop('record', True):
            entities = cls.filter_by(**kwargs).all()
            for entity in entities:
                entity.delete()
        else:
            cls.filter_by(**kwargs).update({cls.DELETED: cls.ID})
        db.session.flush()

    @classmethod
    def physical_delete_by(cls: MODEL, **kwargs):
        """物理删除"""
        cls.filter_by(**kwargs).delete()

    def update(self: MODEL, **kwargs):
        record = kwargs.pop('record', True)
        for attr, value in kwargs.items():
            record and record_update(self, attr, value)
            setattr(self, attr, value)
        self.submit()

    def delete(self: MODEL, record=True):
        """软删除"""
        setattr(self, 'DELETED', self.ID)
        record and record_delete(self)
        self.submit()

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
    ID = db.Column(db.Integer, primary_key=True, comment='主键')
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='版本号')
    DELETED = db.Column(db.Integer, nullable=False, default=0, comment='删除标识')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), default=get_userno_or_default, comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), default=get_userno_or_default, onupdate=get_userno_or_default, comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TSystemOperationLogContent(DBModel, BaseColumn):
    """操作日志内容表"""
    __tablename__ = 'SYSTEM_OPERATION_LOG_CONTENT'
    LOG_NO = db.Column(db.String(64), index=True, nullable=False, comment='日志编号')
    OPERATION_TYPE = db.Column(db.String(32), nullable=False, comment='操作类型(INSERT:新增, UPDATE:修改, DELETE:删除)')
    TABLE_NAME = db.Column(db.String(128), comment='列名')
    ROW_ID = db.Column(db.Integer, comment='新增行或删除行的ID')
    COLUMN_NAME = db.Column(db.String(128), comment='列名')
    OLD_VALUE = db.Column(db.Text, comment='旧值')
    NEW_VALUE = db.Column(db.Text, comment='新值')


def get_trace_id():
    if hasattr(g, 'trace_id'):
        return g.trace_id

    trace_id = getattr(threadlocal, 'trace_id', None)
    if not trace_id:
        trace_id = new_ulid()
        setattr(threadlocal, 'trace_id', trace_id)
    return trace_id


def record_insert(entity):
    """记录新增的行ID"""
    content = TSystemOperationLogContent()
    content.LOG_NO = get_trace_id(),
    content.OPERATION_TYPE = 'INSERT',
    content.TABLE_NAME = entity.__tablename__,
    content.ROW_ID = entity.ID
    db.session.add(content)
    db.session.flush()


def record_update(entity, columnname, new):
    """记录更新数据的旧值和新值"""
    if columnname in ['ID', 'VERSION', 'DELETED', 'REMARK', 'CREATED_BY', 'CREATED_TIME', 'UPDATED_BY', 'UPDATED_TIME']:
        return
    old = getattr(entity, columnname, None)
    if old is None:
        return
    if isinstance(old, (dict, list)):
        old = to_json(old)
    if isinstance(new, (dict, list)):
        new = to_json(new)
    content = TSystemOperationLogContent()
    content.LOG_NO = get_trace_id(),
    content.OPERATION_TYPE = 'UPDATE',
    content.TABLE_NAME = entity.__tablename__,
    content.ROW_ID = entity.ID
    content.COLUMN_NAME = columnname,
    content.OLD_VALUE = old
    content.NEW_VALUE = new
    db.session.add(content)
    db.session.flush()


def record_delete(entity):
    """记录删除的行ID"""
    content = TSystemOperationLogContent()
    content.LOG_NO = get_trace_id(),
    content.OPERATION_TYPE = 'DELETE',
    content.TABLE_NAME = entity.__tablename__,
    content.ROW_ID = entity.ID
    db.session.add(content)
    db.session.flush()
