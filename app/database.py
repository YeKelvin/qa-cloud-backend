#!/usr/bin/ python3
# @File    : database.py
# @Time    : 2019/11/7 10:57
# @Author  : Kelvin.Ye
import decimal

from sqlalchemy import func

from app.extension import db
from app.signals import record_delete_signal
from app.signals import record_insert_signal
from app.signals import record_update_signal
from app.tools.localvars import get_userno_or_default
from app.utils.time_util import datetime_now_by_utc8


MODEL = type[db.Model]


def db_query(*args, **kwargs):
    return db.session.query(*args, **kwargs)


def db_execute(*args, **kwargs):
    return db.session.scalars(*args, **kwargs)


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations"""

    @classmethod
    def exclude_delete(cls):
        return cls.DELETED == 0

    @classmethod
    def insert(cls: MODEL, **kwargs):
        record = kwargs.pop('record', True)
        entity = cls(**kwargs)
        entity.submit()
        record and record_insert_signal.send(entity=entity)

    @classmethod
    def no_record_insert(cls: MODEL, **kwargs):
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
    def sum_by(cls: MODEL, field, where: dict) -> decimal.Decimal:
        """e.g.:

        Table.sum_by(field=xxx, where=dict(xxx=xxx))
        """
        return cls.query.session.query(func.sum(field)).filter_by(DELETED=0, **where).scalar() or 0

    @classmethod
    def avg_by(cls: MODEL, field, **kwargs) -> decimal.Decimal:
        return cls.query.session.query(func.avg(field)).filter_by(DELETED=0, **kwargs).scalar() or 0

    @classmethod
    def updates(cls: MODEL, setter: dict, where: list, record=True):
        """e.g.:

        Table.updates(sette=dict(xxx=xxx), where=[])
        """
        if record:
            entities = cls.filter(*where).all()
            for entity in entities:
                entity.update(**setter)
        else:
            cls.filter(*where).update({getattr(cls, attr): value for attr, value in setter.items()})
        db.session.flush()

    @classmethod
    def updates_by(cls: MODEL, setter: dict, where: dict, record=True):
        """e.g.:

        Table.updates(setter=dict(xxx=xxx), where=dict(xxx=xxx))
        """
        if record:
            entities = cls.filter_by(**where).all()
            for entity in entities:
                entity.update(**setter)
        else:
            cls.filter_by(**where).update({getattr(cls, attr): value for attr, value in setter.items()})
        db.session.flush()

    @classmethod
    def no_record_updates_by(cls: MODEL, setter: dict, where: dict):
        cls.updates_by(setter, where, record=False)

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
        for column, value in kwargs.items():
            record and record_update_signal.send(entity=self, columnname=column, newvalue=value)
            setattr(self, column, value)
        self.submit()

    def no_record_update(self: MODEL, **kwargs):
        kwargs['record'] = False
        self.update(**kwargs)

    def delete(self: MODEL, record=True):
        """软删除"""
        setattr(self, 'DELETED', self.ID)
        record and record_delete_signal.send(entity=self)
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
    UPDATED_BY = db.Column(
        db.String(64),
        default=get_userno_or_default,
        onupdate=get_userno_or_default,
        comment='更新人'
    )
    UPDATED_TIME = db.Column(
        db.DateTime,
        default=datetime_now_by_utc8,
        onupdate=datetime_now_by_utc8,
        comment='更新时间'
    )
