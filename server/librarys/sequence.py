#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sequence.py
# @Time    : 2019/11/7 14:10
# @Author  : Kelvin.Ye
from datetime import datetime

from server.database import DBModel, db
from server.librarys.exception import ServiceError
from server.utils import config
from server.utils.log_util import get_logger

log = get_logger(__name__)


class TSequence(DBModel):
    __tablename__ = 'sequence'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    SEQ_NAME = db.Column(db.String(128), index=True, unique=True, nullable=False, comment='序列名称')
    CURRENT_VAL = db.Column(db.Integer, nullable=False, default=0, comment='当前序列值')
    MIN_VAL = db.Column(db.Integer, nullable=False, default=0, comment='序列最小值')
    MAX_VAL = db.Column(db.Integer, nullable=False, default=999999999, comment='序列最大值')
    INCREMENT = db.Column(db.Integer, nullable=False, default=1, comment='序列步长')
    LOOP = db.Column(db.Boolean, nullable=False, default=False, comment='序列是否循环')
    LOOP_COUNT = db.Column(db.Integer, nullable=False, default=0, comment='序列允许循环次数')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    @staticmethod
    def next_val(seq_name):
        """获取序列下一个值

        Returns: 序列下一个值

        """
        sequence = TSequence.query.filter_by(SEQ_NAME=seq_name).first()
        # 判断序列当前值是否已达最大值
        if sequence.CURRENT_VAL == sequence.MAX_VAL:
            # 如序列允许循环则当前值赋值最小值，否则抛异常
            if sequence.LOOP:
                next_value = sequence.MIN_VAL
                sequence.LOOP_COUNT = sequence.LOOP_COUNT + 1
            else:
                raise ServiceError(f'{seq_name}序列已达最大值')
        else:
            # 序列未达最大值，按步长增长
            next_value = sequence.CURRENT_VAL + sequence.INCREMENT

        sequence.CURRENT_VAL = next_value
        db.session.commit()
        return next_value

    @staticmethod
    def curr_val(seq_name):
        """获取序列当前值

        Returns: 序列当前值

        """
        sequence = TSequence.query.filter_by(SEQ_NAME=seq_name).first()
        return sequence.CURRENT_VAL


class SqliteSequence:
    def __init__(self, seq_name):
        self.seq_name = seq_name

    def next_value(self):
        return TSequence.next_val(self.seq_name)

    def curr_value(self):
        return TSequence.curr_val(self.seq_name)


class SqlalchemySequence:
    def __init__(self, seq_name):
        from sqlalchemy import Sequence
        self.seq_name = seq_name
        self.sequence = Sequence(seq_name)

    def next_value(self):
        return self.sequence.NEXT_VALUE

    def curr_value(self):
        pass


if not config.get('db', 'type').startswith('sqlite'):
    Sequence = SqlalchemySequence
else:
    Sequence = SqliteSequence
