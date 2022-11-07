#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : notification_robot_dao.py
# @Time    : 2022-05-07 22:32:45
# @Author  : Kelvin.Ye
from flask_sqlalchemy import Pagination

from app.public.model import TNotificationRobot
from app.utils.sqlalchemy_util import QueryCondition


def select_first(**kwargs) -> TNotificationRobot:
    return TNotificationRobot.filter_by(**kwargs).first()


def select_by_no(robot_no) -> TNotificationRobot:
    return TNotificationRobot.filter_by(ROBOT_NO=robot_no).first()


def select_by_name(robot_name) -> TNotificationRobot:
    return TNotificationRobot.filter_by(ROBOT_NAME=robot_name).first()


def select_by_name_and_type(robot_name, robot_type) -> TNotificationRobot:
    return TNotificationRobot.filter_by(ROBOT_NAME=robot_name, ROBOT_TYPE=robot_type).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    conds.like(TNotificationRobot.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
    conds.like(TNotificationRobot.ROBOT_NO, kwargs.pop('robotNo', None))
    conds.like(TNotificationRobot.ROBOT_NAME, kwargs.pop('robotName', None))
    conds.like(TNotificationRobot.ROBOT_DESC, kwargs.pop('robotDesc', None))
    conds.like(TNotificationRobot.ROBOT_TYPE, kwargs.pop('robotType', None))
    conds.like(TNotificationRobot.STATE, kwargs.pop('state', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return (
        TNotificationRobot
        .filter(*conds)
        .order_by(TNotificationRobot.CREATED_TIME.desc())
        .paginate(page=page, per_page=page_size)
    )
