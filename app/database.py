#!/usr/bin/ python3
# @File    : database.py
# @Time    : 2019/11/7 10:57
# @Author  : Kelvin.Ye
import decimal

from typing import TypeVar

from sqlalchemy import ScalarResult
from sqlalchemy import func
from sqlalchemy.orm import Query

from app.extension import db
from app.signals import record_delete_signal
from app.signals import record_insert_signal
from app.signals import record_update_signal
from app.tools.localvars import get_userno_or_default
from app.utils.time_util import datetime_now_by_utc8


T = TypeVar('T', bound='TableModel')


def db_query(*args, **kwargs):
    return db.session.query(*args, **kwargs)


def db_execute(*args, **kwargs):
    return db.session.execute(*args, **kwargs)


def db_scalars(*args, **kwargs) -> ScalarResult:
    return db.session.scalars(*args, **kwargs)


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations"""

    @classmethod
    def get_by_id(cls: type[T], entity_id: str) -> T:
        """根据ID获取数据"""
        return cls.query.get(entity_id)

    @classmethod
    def exclude_deleted_data(cls: type[T]):
        """排除已删除的数据条件"""
        return cls.DELETED == 0

    @classmethod
    def filter(cls: type[T], *args) -> Query:
        """查询"""
        return cls.query.filter(cls.DELETED == 0, *args)

    @classmethod
    def filter_by(cls: type[T], **kwargs) -> Query:
        """查询"""
        return cls.query.filter_by(DELETED=0, **kwargs)

    @classmethod
    def count_by(cls: type[T], **kwargs) -> int:
        """计数"""
        return db.session.query(func.count(cls.ID)).filter_by(DELETED=0, **kwargs).scalar() or 0

    @classmethod
    def sum_by(cls: type[T], field, where: dict) -> decimal.Decimal:
        """合计

        e.g.:
        Table.sum_by(field=xxx, where=dict(xxx=xxx))
        """
        return db.session.query(func.sum(field)).filter_by(DELETED=0, **where).scalar() or 0

    @classmethod
    def avg_by(cls: type[T], field, **kwargs) -> decimal.Decimal:
        """求平均值"""
        return db.session.query(func.avg(field)).filter_by(DELETED=0, **kwargs).scalar() or 0

    @classmethod
    def insert(cls: type[T], **kwargs):
        """插入数据"""
        record = kwargs.pop('record', True)
        entity = cls(**kwargs)
        entity.submit()
        record and record_insert_signal.send(entity=entity)

    @classmethod
    def norecord_insert(cls: type[T], **kwargs):
        """无记录插入"""
        kwargs['record'] = False
        cls.insert(**kwargs)

    @classmethod
    def updates(cls: type[T], values: dict, where: list, record=True):
        """批量更新

        e.g.:
        Table.updates(values=dict(xxx=xxx), where=[])
        """
        if record:
            entities = cls.filter(*where).all()
            for entity in entities:
                entity.update(**values)
        else:
            cls.filter(*where).update({getattr(cls, attr): value for attr, value in values.items()})
        db.session.flush()

    @classmethod
    def updates_by(cls: type[T], values: dict, where: dict, record=True):
        """批量更新

        e.g.:
        Table.updates(values=dict(xxx=xxx), where=dict(xxx=xxx))
        """
        if record:
            entities = cls.filter_by(**where).all()
            for entity in entities:
                entity.update(**values)
        else:
            cls.filter_by(**where).update({getattr(cls, attr): value for attr, value in values.items()})
        db.session.flush()

    @classmethod
    def norecord_updates_by(cls: type[T], values: dict, where: dict):
        """无记录批量更新"""
        cls.updates_by(values, where, record=False)

    @classmethod
    def deletes(cls: type[T], *args, record=True):
        """批量删除"""
        if record:
            entities = cls.filter(*args).all()
            for entity in entities:
                entity.delete()
        else:
            cls.filter(*args).update({cls.DELETED: cls.ID})
        db.session.flush()

    @classmethod
    def deletes_by(cls: type[T], **kwargs):
        """批量删除"""
        if kwargs.pop('record', True):
            entities = cls.filter_by(**kwargs).all()
            for entity in entities:
                entity.delete()
        else:
            cls.filter_by(**kwargs).update({cls.DELETED: cls.ID})
        db.session.flush()

    def update(self, **kwargs):
        """更新"""
        record = kwargs.pop('record', True)
        for column, value in kwargs.items():
            record and record_update_signal.send(entity=self, columnname=column, newvalue=value)
            setattr(self, column, value)
        self.submit()

    def norecord_update(self, **kwargs):
        """无记录更新"""
        kwargs['record'] = False
        self.update(**kwargs)

    def delete(self, physical=False, record=True):
        """逻辑删除"""
        record and record_delete_signal.send(entity=self)
        if not physical:
            setattr(self, 'DELETED', self.ID)
        else:
            super().delete()
        self.submit()

    def norecord_delete(self, physical=False):
        """无记录删除"""
        self.delete(physical=physical, record=False)

    def physical_delete(self, record=True):
        """物理删除"""
        self.delete(physical=True, record=record)

    def submit(self):
        """写入数据"""
        db.session.add(self)
        db.session.flush()

    def save(self, commit=True):
        """提交数据"""
        db.session.add(self)
        db.session.flush()
        if commit:
            db.session.commit()


class TableModel(CRUDMixin, db.Model):

    __abstract__ = True

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class BaseColumn:
    # TODO: 移至TableModel
    ID = db.Column(db.Integer(), primary_key=True, comment='主键')
    VERSION = db.Column(db.Integer(), nullable=False, default=0, comment='版本号')
    DELETED = db.Column(db.Integer(), nullable=False, default=0, comment='删除标识')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), default=get_userno_or_default, comment='创建人')
    CREATED_TIME = db.Column(db.DateTime(), default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(
        db.String(64),
        default=get_userno_or_default,
        onupdate=get_userno_or_default,
        comment='更新人'
    )
    UPDATED_TIME = db.Column(
        db.DateTime(),
        default=datetime_now_by_utc8,
        onupdate=datetime_now_by_utc8,
        comment='更新时间'
    )
