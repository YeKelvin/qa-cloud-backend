#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : message_service.py
# @Time    : 2022-05-07 22:32:17
# @Author  : Kelvin.Ye
from app.public.dao import notification_robot_dao as NotificationRobotDao
from app.public.enum import RobotState
from app.public.model import TNotificationRobot
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_notice_robot_list(req):
    # 查询机器人列表
    pagination = NotificationRobotDao.select_list(
        workspaceNo=req.workspaceNo,
        robotNo=req.robotNo,
        robotName=req.robotName,
        robotDesc=req.robotDesc,
        robotType=req.robotType,
        state=req.state,
        page=req.page,
        pageSize=req.pageSize
    )

    data = [
        {
            'robotNo': robot.ROBOT_NO,
            'robotName': robot.ROBOT_NAME,
            'robotDesc': robot.ROBOT_DESC,
            'robotType': robot.ROBOT_TYPE,
            'state': robot.STATE
        }
        for robot in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


@http_service
def query_notice_robot_all(req):
    # 查询所有机器人
    conds = QueryCondition()
    conds.equal(TNotificationRobot.WORKSPACE_NO, req.workspaceNo)
    robots = TNotificationRobot.filter(*conds).order_by(TNotificationRobot.CREATED_TIME.desc()).all()

    return [
        {
            'robotNo': robot.ROBOT_NO,
            'robotName': robot.ROBOT_NAME,
            'robotDesc': robot.ROBOT_DESC,
            'robotType': robot.ROBOT_TYPE,
            'state': robot.STATE
        }
        for robot in robots
    ]


@http_service
def query_notice_robot(req):
    # 查询机器人
    robot = NotificationRobotDao.select_by_no(req.robotNo)
    check_exists(robot, error_msg='机器人不存在')

    return {
        'workspaceNo': robot.WORKSPACE_NO,
        'robotNo': robot.ROBOT_NO,
        'robotName': robot.ROBOT_NAME,
        'robotDesc': robot.ROBOT_DESC,
        'robotType': robot.ROBOT_TYPE,
        'robotConfig': robot.ROBOT_CONFIG,
        'state': robot.STATE
    }


@http_service
@transactional
def create_notice_robot(req):
    # 空间编号不能为空
    if not req.workspaceNo:
        raise ServiceError('空间编号不能为空')

    # 查询机器人
    robot = NotificationRobotDao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        ROBOT_NAME=req.robotName,
        ROBOT_TYPE=req.robotType
    )
    check_not_exists(robot, error_msg='机器人已存在')

    # 新增机器人
    robot_no = new_id()
    TNotificationRobot.insert(
        WORKSPACE_NO=req.workspaceNo,
        ROBOT_NO=robot_no,
        ROBOT_NAME=req.robotName,
        ROBOT_DESC=req.robotDesc,
        ROBOT_TYPE=req.robotType,
        ROBOT_CONFIG=req.robotConfig,
        STATE=RobotState.ENABLE.value
    )

    return {'robotNo': robot_no}


@http_service
@transactional
def modify_notice_robot(req):
    # 查询机器人
    robot = NotificationRobotDao.select_by_no(req.robotNo)
    check_exists(robot, error_msg='机器人不存在')

    # 唯一性校验
    if robot.ROBOT_NAME != req.robotName and NotificationRobotDao.select_first(
        WORKSPACE_NO=robot.WORKSPACE_NO,
        ROBOT_NAME=req.robotName,
        ROBOT_TYPE=robot.ROBOT_TYPE
    ):
        raise ServiceError('机器人名称已存在')

    # 更新机器人信息
    robot.update(
        ROBOT_NAME=req.robotName,
        ROBOT_DESC=req.robotDesc,
        ROBOT_CONFIG=req.robotConfig
    )


@http_service
@transactional
def modify_notice_robot_state(req):
    # 查询机器人
    robot = NotificationRobotDao.select_by_no(req.robotNo)
    check_exists(robot, error_msg='机器人不存在')

    # 更新机器人状态
    robot.update(STATE=req.state)


@http_service
@transactional
def remove_notice_robot(req):
    # 查询机器人
    robot = NotificationRobotDao.select_by_no(req.robotNo)
    check_exists(robot, error_msg='机器人不存在')

    # 删除机器人
    robot.delete()
