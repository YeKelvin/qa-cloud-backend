#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : schedule_job_dao.py
# @Time    : 2022/5/13 15:26
# @Author  : Kelvin.Ye
from app.schedule.model import TScheduleJob


def select_first(**kwargs) -> TScheduleJob:
    return TScheduleJob.filter_by(**kwargs).first()


def select_by_no(job_no) -> TScheduleJob:
    return TScheduleJob.filter_by(JOB_NO=job_no).first()
