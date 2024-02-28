#!/usr/bin/ python3
# @File    : message_service.py
# @Time    : 2022-05-07 22:32:17
# @Author  : Kelvin.Ye
from app.modules.public.dao import notice_robot_dao
from app.modules.public.enum import RobotState
from app.modules.public.model import TNoticeRobot
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_notice_robot_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.like(TNoticeRobot.WORKSPACE_NO, req.workspaceNo)
    conds.like(TNoticeRobot.ROBOT_NO, req.robotNo)
    conds.like(TNoticeRobot.ROBOT_NAME, req.robotName)
    conds.like(TNoticeRobot.ROBOT_DESC, req.robotDesc)
    conds.like(TNoticeRobot.ROBOT_TYPE, req.robotType)
    conds.like(TNoticeRobot.STATE, req.state)

    # 查询机器人列表
    pagination = (
        TNoticeRobot
        .filter(*conds)
        .order_by(TNoticeRobot.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
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

    return {'list': data, 'total': pagination.total}


@http_service
def query_notice_robot_all(req):
    # 查询所有机器人
    conds = QueryCondition()
    conds.equal(TNoticeRobot.WORKSPACE_NO, req.workspaceNo)
    robots = TNoticeRobot.filter(*conds).order_by(TNoticeRobot.CREATED_TIME.desc()).all()

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
    robot = notice_robot_dao.select_by_no(req.robotNo)
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
def create_notice_robot(req):
    # 空间编号不能为空
    if not req.workspaceNo:
        raise ServiceError('空间编号不能为空')

    # 查询机器人
    robot = notice_robot_dao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        ROBOT_NAME=req.robotName,
        ROBOT_TYPE=req.robotType
    )
    check_not_exists(robot, error_msg='机器人已存在')

    # 新增机器人
    robot_no = new_id()
    TNoticeRobot.insert(
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
def modify_notice_robot(req):
    # 查询机器人
    robot = notice_robot_dao.select_by_no(req.robotNo)
    check_exists(robot, error_msg='机器人不存在')

    # 唯一性校验
    if robot.ROBOT_NAME != req.robotName and notice_robot_dao.select_first(
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
def modify_notice_robot_state(req):
    # 查询机器人
    robot = notice_robot_dao.select_by_no(req.robotNo)
    check_exists(robot, error_msg='机器人不存在')

    # 更新机器人状态
    robot.update(STATE=req.state)


@http_service
def remove_notice_robot(req):
    # 查询机器人
    robot = notice_robot_dao.select_by_no(req.robotNo)
    check_exists(robot, error_msg='机器人不存在')

    # 删除机器人
    robot.delete()
