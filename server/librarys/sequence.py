#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sequence.py
# @Time    : 2019/11/7 14:10
# @Author  : Kelvin.Ye
from datetime import datetime

from server.database import Model, db
from server.librarys.exception import ServiceError
from server.utils import config
from server.utils.log_util import get_logger

log = get_logger(__name__)


class TSequence(Model):
    __tablename__ = 't_sequence'
    id = db.Column(db.Integer, primary_key=True)
    seq_name = db.Column(db.String(128), index=True, unique=True, nullable=False, comment='序列名称')
    current_val = db.Column(db.Integer, nullable=False, default=0, comment='当前序列值')
    min_val = db.Column(db.Integer, nullable=False, default=0, comment='序列最小值')
    max_val = db.Column(db.Integer, nullable=False, default=999999999, comment='序列最大值')
    increment = db.Column(db.Integer, nullable=False, default=1, comment='序列步长')
    loop = db.Column(db.Boolean, nullable=False, default=False, comment='序列是否循环')
    loop_count = db.Column(db.Integer, nullable=False, default=0, comment='序列允许循环次数')
    remark = db.Column(db.String(128), comment='备注')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, default=datetime.now(), comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')

    @staticmethod
    def next_val(seq_name):
        """获取序列下一个值

        Returns: 序列下一个值

        """
        sequence = TSequence.query.filter_by(seq_name=seq_name).first()
        # 判断序列当前值是否已达最大值
        if sequence.current_val == sequence.max_val:
            # 如序列允许循环则当前值赋值最小值，否则抛异常
            if sequence.loop:
                next_value = sequence.min_val
                sequence.loop_count = sequence.loop_count + 1
            else:
                raise ServiceError(f'{seq_name}序列已达最大值')
        else:
            # 序列未达最大值，按步长增长
            next_value = sequence.current_val + sequence.increment

        sequence.current_val = next_value
        db.session.commit()
        return next_value

    @staticmethod
    def curr_val(seq_name):
        """获取序列当前值

        Returns: 序列当前值

        """
        sequence = TSequence.query.filter_by(seq_name=seq_name).first()
        return sequence.current_val


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
        return self.sequence.next_value

    def curr_value(self):
        pass


if not config.get('db', 'type').startswith('sqlite'):
    Sequence = SqlalchemySequence
else:
    Sequence = SqliteSequence
