#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2022/5/13 14:48
# @Author  : Kelvin.Ye
from sqlalchemy.dialects.postgresql import JSONB

from app.database import BaseColumn
from app.database import DBModel
from app.database import db


class TScheduleJob(DBModel, BaseColumn):
    """定时任务表"""
    __tablename__ = 'SCHEDULE_JOB'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    JOB_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='作业编号')
    JOB_NAME = db.Column(db.String(128), nullable=False, comment='作业名称')
    JOB_DESC = db.Column(db.String(256), comment='作业描述')
    JOB_TYPE = db.Column(db.String(32), nullable=False, comment='作业类型(TESTPLAN, COLLECTION, GROUP)')
    JOB_ARGS = db.Column(JSONB, nullable=False, comment='作业参数')
    TRIGGER_TYPE = db.Column(db.String(32), nullable=False, comment='触发器类型(DATE, INTERVAL, CRON)')
    TRIGGER_ARGS = db.Column(JSONB, nullable=False, comment='触发器参数')
    STATE = db.Column(db.String(16), nullable=False, default='NORMAL', comment='用户状态(NORMAL, PAUSED, CLOSED)')
    PAUSE_BY = db.Column(db.String(64), comment='暂停人')
    PAUSE_TIME = db.Column(db.DateTime, comment='暂停时间')
    RESUME_BY = db.Column(db.String(64), comment='恢复人')
    RESUME_TIME = db.Column(db.DateTime, comment='恢复时间')
    CLOSE_BY = db.Column(db.String(64), comment='关闭人')
    CLOSE_TIME = db.Column(db.DateTime, comment='关闭时间')
