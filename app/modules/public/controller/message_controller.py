#!/usr/bin/ python3
# @File    : message_controller.py
# @Time    : 2022-05-07 22:32:14
# @Author  : Kelvin.Ye
from app.modules.public.controller import blueprint
from app.modules.public.enum import RobotState
from app.modules.public.enum import RobotType
from app.modules.public.service import message_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/notice/robot/list')
@require_login
@require_permission('QUERY_ROBOT')
def query_notice_robot_list():
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
    return service.query_notice_robot_list(req)


@blueprint.get('/notice/robot/all')
@require_login
@require_permission('QUERY_ROBOT')
def query_notice_robot_all():
    """查询全部通知机器人"""
    req = JsonParser(
        Argument('workspaceNo')
    ).parse()
    return service.query_notice_robot_all(req)


@blueprint.get('/notice/robot')
@require_login
@require_permission('QUERY_ROBOT')
def query_notice_robot():
    """查询通知机器人"""
    req = JsonParser(
        Argument('robotNo', required=True, nullable=False, help='机器人编号不能为空')
    ).parse()
    return service.query_notice_robot(req)


@blueprint.post('/notice/robot')
@require_login
@require_permission('CREATE_ROBOT')
def create_notice_robot():
    """新增通知机器人"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('robotName', required=True, nullable=False, help='机器人名称不能为空'),
        Argument('robotDesc'),
        Argument('robotType', required=True, nullable=False, enum=RobotType, help='机器人类型不能为空'),
        Argument('robotConfig', required=True, nullable=False, help='机器人配置不能为空'),
    ).parse()
    return service.create_notice_robot(req)


@blueprint.put('/notice/robot')
@require_login
@require_permission('MODIFY_ROBOT')
def modify_notice_robot():
    """修改通知机器人"""
    req = JsonParser(
        Argument('robotNo', required=True, nullable=False, help='机器人编号不能为空'),
        Argument('robotName', required=True, nullable=False, help='机器人名称不能为空'),
        Argument('robotDesc'),
        Argument('robotConfig', required=True, nullable=False, help='机器人配置不能为空'),
    ).parse()
    return service.modify_notice_robot(req)


@blueprint.put('/notice/robot/state')
@require_login
@require_permission('MODIFY_ROBOT')
def modify_notice_robot_state():
    """修改通知机器人状态"""
    req = JsonParser(
        Argument('robotNo', required=True, nullable=False, help='机器人编号不能为空'),
        Argument('state', required=True, nullable=False, enum=RobotState, help='通知机器人状态不能为空')
    ).parse()
    return service.modify_notice_robot_state(req)


@blueprint.delete('/notice/robot')
@require_login
@require_permission('REMOVE_ROBOT')
def remove_notice_robot():
    """删除通知机器人"""
    req = JsonParser(
        Argument('robotNo', required=True, nullable=False, help='机器人编号不能为空')
    ).parse()
    return service.remove_notice_robot(req)
