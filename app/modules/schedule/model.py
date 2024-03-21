#!/usr/bin/ python3
# @File    : model.py
# @Time    : 2022/5/13 14:48
# @Author  : Kelvin.Ye
from sqlalchemy.dialects.postgresql import JSONB

from app.database import BaseColumn
from app.database import TableModel
from app.database import db


class TScheduleJob(TableModel, BaseColumn):
    """定时任务表"""
    __tablename__ = 'SCHEDULE_JOB'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    JOB_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='作业编号')
    JOB_NAME = db.Column(db.String(128), nullable=False, comment='作业名称')
    JOB_DESC = db.Column(db.String(256), comment='作业描述')
    JOB_TYPE = db.Column(db.String(32), nullable=False, comment='作业类型(COLLECTION, TESTCASE, TESTPLAN)')
    JOB_ARGS = db.Column(JSONB, nullable=False, comment='作业参数')
    JOB_STATE = db.Column(
        db.String(16), nullable=False, default='PENDING', comment='作业状态(PENDING, RUNNING, PAUSED, CLOSED)'
    )
    TRIGGER_TYPE = db.Column(db.String(32), nullable=False, comment='触发器类型(DATE, CRON)')
    TRIGGER_ARGS = db.Column(JSONB, nullable=False, comment='触发器参数')


class TScheduleLog(TableModel, BaseColumn):
    """定时任务触发日志表"""
    __tablename__ = 'SCHEDULE_LOG'
    LOG_NO = db.Column(db.String(32), index=True, nullable=False, comment='日志编号')
    JOB_NO = db.Column(db.String(32), index=True, nullable=False, comment='作业编号')
    JOB_EVENT = db.Column(db.String(32), comment='作业事件(ADD, MODIFY, EXECUTE, PAUSE, RESUME, CLOSE)')
    OPERATION_BY = db.Column(db.String(64), comment='操作人')
    OPERATION_TIME = db.Column(db.DateTime(), comment='操作时间')
