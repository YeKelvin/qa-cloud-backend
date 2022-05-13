#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : job_service.py
# @Time    : 2022/5/13 14:50
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.exceptions import ServiceError
from app.common.identity import new_id
from app.common.validator import check_exists
from app.common.validator import check_not_exists
from app.schedule.dao import schedule_job_dao as ScheduleJobDao
from app.schedule.enum import JobType
from app.schedule.enum import TriggerType
from app.schedule.model import TScheduleJob
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_schedule_job_list(req):
    ...


@http_service
def query_schedule_job_all(req):
    ...


@http_service
def query_schedule_job_info(req):
    ...


@http_service
def create_schedule_job(req):
    ...


@http_service
def modify_schedule_job(req):
    ...


@http_service
def pause_schedule_job(req):
    ...


@http_service
def resume_schedule_job(req):
    ...


@http_service
def shutdown_schedule_job(req):
    ...
