#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : notification_controller.py
# @Time    : 2022-05-07 22:32:14
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.public.controller import blueprint
from app.public.enum import RobotType
from app.public.enum import RobotState
from app.public.service import notification_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/notification/robot/list')
@require_login
@require_permission
def query_notification_robot_list():
    """分页查询通知机器人列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('robotNo'),
        Argument('robotName'),
        Argument('robotDesc'),
        Argument('robotType'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_notification_robot_list(req)


@blueprint.get('/notification/robot/all')
@require_login
@require_permission
def query_notification_robot_all():
    """查询所有通知机器人"""
    req = JsonParser(
        Argument('workspaceNo')
    ).parse()
    return service.query_notification_robot_all(req)


@blueprint.get('/notification/robot')
@require_login
@require_permission
def query_notification_robot():
    """查询通知机器人"""
    req = JsonParser(
        Argument('robotNo', required=True, nullable=False, help='机器人编号不能为空')
    ).parse()
    return service.query_notification_robot(req)


@blueprint.post('/notification/robot')
@require_login
@require_permission
def create_notification_robot():
    """新增通知机器人"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('robotName', required=True, nullable=False, help='机器人名称不能为空'),
        Argument('robotDesc'),
        Argument('robotType', required=True, nullable=False, enum=RobotType, help='机器人类型不能为空'),
        Argument('robotConfig', required=True, nullable=False, help='机器人配置不能为空'),
    ).parse()
    return service.create_notification_robot(req)


@blueprint.put('/notification/robot')
@require_login
@require_permission
def modify_notification_robot():
    """修改通知机器人"""
    req = JsonParser(
        Argument('robotNo', required=True, nullable=False, help='机器人编号不能为空'),
        Argument('robotName', required=True, nullable=False, help='机器人名称不能为空'),
        Argument('robotDesc'),
        Argument('robotConfig', required=True, nullable=False, help='机器人配置不能为空'),
    ).parse()
    return service.modify_notification_robot(req)


@blueprint.patch('/notification/robot/state')
@require_login
@require_permission
def modify_notification_robot_state():
    """修改通知机器人状态"""
    req = JsonParser(
        Argument('robotNo', required=True, nullable=False, help='机器人编号不能为空'),
        Argument('state', required=True, nullable=False, enum=RobotState, help='通知机器人状态不能为空')
    ).parse()
    return service.modify_notification_robot_state(req)


@blueprint.delete('/notification/robot')
@require_login
@require_permission
def remove_notification_robot():
    """删除通知机器人"""
    req = JsonParser(
        Argument('robotNo', required=True, nullable=False, help='机器人编号不能为空')
    ).parse()
    return service.remove_notification_robot(req)
