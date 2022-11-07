#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : schedule_job_dao.py
# @Time    : 2022/5/13 15:26
# @Author  : Kelvin.Ye
from flask_sqlalchemy import Pagination

from app.schedule.model import TScheduleJob
from app.utils.sqlalchemy_util import QueryCondition


def select_first(**kwargs) -> TScheduleJob:
    return TScheduleJob.filter_by(**kwargs).first()


def select_by_no(job_no) -> TScheduleJob:
    return TScheduleJob.filter_by(JOB_NO=job_no).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    conds.like(TScheduleJob.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
    conds.like(TScheduleJob.JOB_NO, kwargs.pop('jobNo', None))
    conds.like(TScheduleJob.JOB_NAME, kwargs.pop('jobName', None))
    conds.like(TScheduleJob.JOB_DESC, kwargs.pop('jobDesc', None))
    conds.like(TScheduleJob.JOB_TYPE, kwargs.pop('jobType', None))
    conds.like(TScheduleJob.TRIGGER_TYPE, kwargs.pop('triggerType', None))
    conds.like(TScheduleJob.STATE, kwargs.pop('state', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return (
        TScheduleJob
        .filter(*conds)
        .order_by(TScheduleJob.CREATED_TIME.desc())
        .paginate(page=page, per_page=page_size)
    )
