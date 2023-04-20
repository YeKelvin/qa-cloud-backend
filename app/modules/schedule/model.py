#!/usr/bin/ python3
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


class TScheduleJobLog(DBModel, BaseColumn):
    """定时任务日志表"""
    __tablename__ = 'SCHEDULE_JOB_LOG'
    JOB_NO = db.Column(db.String(32), index=True, nullable=False, comment='作业编号')
    LOG_NO = db.Column(db.String(32), index=True, nullable=False, comment='日志编号')
    OPERATION_TYPE = db.Column(db.String(32), comment='操作类型(ADD, MODIFY, EXECUTE, PAUSE, RESUME, CLOSE)')
    OPERATION_BY = db.Column(db.String(64), comment='操作人')
    OPERATION_TIME = db.Column(db.DateTime, comment='操作时间')
    OPERATION_ARGS = db.Column(JSONB, comment='操作参数')


class TScheduleJobChangeDetails(DBModel, BaseColumn):
    """定时任务变更详情表"""
    __tablename__ = 'SCHEDULE_JOB_CHANGE_DETAILS'
    CHANGE_TYPE = db.Column(db.String(32), comment='参数类型(JOB, TRIGGER)')
    CHANGE_FROM = db.Column(JSONB, nullable=False, comment='变更前的参数')
    CHANGE_TO = db.Column(JSONB, nullable=False, comment='变更后的参数')
