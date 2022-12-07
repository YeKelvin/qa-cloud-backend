#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : command.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
import click
from flask.cli import with_appcontext

from app.database import TSystemOperationLogContent  # noqa
from app.extension import db  # noqa
from app.public.model import TWorkspace  # noqa
from app.public.model import TWorkspaceUser  # noqa
from app.script.model import TVariableDataset  # noqa
from app.tools.identity import new_id
from app.tools.logger import get_logger
from app.usercenter.model import TApi  # noqa
from app.usercenter.model import TPermission  # noqa
from app.usercenter.model import TPermissionModule  # noqa
from app.usercenter.model import TPermissionObject  # noqa
from app.usercenter.model import TRole  # noqa
from app.usercenter.model import TUser  # noqa
from app.usercenter.model import TUserLoginInfo  # noqa
from app.usercenter.model import TUserPassword  # noqa
from app.usercenter.model import TUserRole  # noqa
from app.utils.security import encrypt_password


from app.script.model import *  # noqa isort:skip
from app.system.model import *  # noqa isort:skip
from app.public.model import *  # noqa isort:skip
from app.usercenter.model import *  # noqa isort:skip


log = get_logger(__name__)


@click.command()
def newid():
    click.echo(new_id())


@click.command()
@with_appcontext
def initdb():
    """创建表"""
    db.create_all()
    click.echo('创建所有数据库表成功')


@click.command()
@click.option('-m', '--confirm', help='删除所有表，删除前需要输入确认信息，注意：该命令仅用于开发环境！！！')
@with_appcontext
def dropdb(confirm):
    if not confirm:
        click.echo('请输入删除表格的确认信息')
        return
    if confirm != 'only use on development!!!':
        click.echo('确认信息不正确，请重试')
        return
    db.drop_all()
    click.echo('删除所有数据库表成功')


@click.command()
def initdata():
    """初始化数据"""
    init_user()
    init_role()
    init_permission()
    init_user_role()
    init_global_variable_dataset()
    click.echo('初始化数据成功')


@with_appcontext
def init_user():
    """初始化用户"""
    # 创建系统用户
    TUser.insert_without_record(USER_NO='9999', USER_NAME='系统')
    # 创建管理员用户
    user_no = new_id()
    TUser.insert_without_record(USER_NO=user_no, USER_NAME='超级管理员')
    TUserLoginInfo.insert_without_record(USER_NO=user_no, LOGIN_NAME='admin', LOGIN_TYPE='ACCOUNT')
    TUserPassword.insert_without_record(
        USER_NO=user_no,
        PASSWORD=encrypt_password('admin', 'admin'),
        PASSWORD_TYPE='LOGIN',
        ERROR_TIMES=0,
        CREATE_TYPE='CUSTOMER'
    )
    # 创建管理员空间
    worksapce_no = new_id()
    TWorkspace.insert_without_record(
        WORKSPACE_NO=worksapce_no,
        WORKSPACE_NAME='超级管理员的个人空间',
        WORKSPACE_SCOPE='PRIVATE'
    )
    TWorkspaceUser.insert_without_record(WORKSPACE_NO=worksapce_no, USER_NO=user_no)
    click.echo('创建初始用户成功')


@with_appcontext
def init_role():
    """初始化角色"""
    create_role(name='超级管理员', code='SUPER_ADMIN', rank='9999')
    create_role(name='系统管理员', code='ADMIN', rank='9000')
    create_role(name='空间管理员', code='WORKSPACE', rank='2000')
    create_role(name='组长', code='GROUP', rank='1000')
    create_role(name='用户', code='GENERAL', rank='1')

    click.echo('创建角色成功')


@click.command()
@with_appcontext
def init_permission():
    init_permission_module()
    init_permission_object()
    init_api()
    click.echo('创建权限成功')


@with_appcontext
def init_permission_module():
    TPermissionModule.insert_without_record(MODULE_NO=new_id(), MODULE_NAME='用户中心', MODULE_CODE='USERCENTER')
    TPermissionModule.insert_without_record(MODULE_NO=new_id(), MODULE_NAME='系统', MODULE_CODE='SYSTEM')
    TPermissionModule.insert_without_record(MODULE_NO=new_id(), MODULE_NAME='公共', MODULE_CODE='PUBLIC')
    TPermissionModule.insert_without_record(MODULE_NO=new_id(), MODULE_NAME='脚本', MODULE_CODE='SCRIPT')
    TPermissionModule.insert_without_record(MODULE_NO=new_id(), MODULE_NAME='调度', MODULE_CODE='SCHEDULER')
    click.echo('创建权限模块成功')


@with_appcontext
def init_permission_object():
    # USERCENTER
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='用户', OBJECT_CODE='USER')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='分组', OBJECT_CODE='GROUP')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='角色', OBJECT_CODE='ROLE')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='权限', OBJECT_CODE='PERMISSION')
    # SYSTEM
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='日志', OBJECT_CODE='LOG')
    # PUBLIC
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='空间', OBJECT_CODE='WORKSPACE')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='标签', OBJECT_CODE='TAG')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='消息', OBJECT_CODE='MESSAGE')
    # SCRIPT
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='元素', OBJECT_CODE='ELEMENT')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='变量', OBJECT_CODE='VARIABLE')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='HTTP请求头', OBJECT_CODE='HTTP_HEADER')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='数据库', OBJECT_CODE='DATABASE')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='测试计划', OBJECT_CODE='TESTPLAN')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='测试报告', OBJECT_CODE='TESTREPORT')
    # SCHEDULE
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='定时任务', OBJECT_CODE='TASK')
    TPermissionObject.insert_without_record(OBJECT_NO=new_id(), OBJECT_NAME='定时作业', OBJECT_CODE='JOB')

    click.echo('创建权限对象成功')


@with_appcontext
def init_api():
    """初始化接口"""
    """
    # 遍历所有接口
    import flask
    app = flask.current_app._get_current_object()
    for rule in app.url_map.iter_rules():
        print(rule)
    """
    # user
    create_api('USERCENTER', 'USER', '用户注册', 'REGISTER', 'CREATE', name='用户注册', method='POST', path='/usercenter/user/register')
    create_api('USERCENTER', 'USER', '重置密码', 'RESET_PASSWORD', 'MODIFY', name='重置密码', method='PATCH', path='/usercenter/user/password/reset')
    create_api('USERCENTER', 'USER', '查询用户', 'QUERY_USER', 'QUERY', name='分页查询用户列表', method='GET', path='/usercenter/user/list')
    create_api('USERCENTER', 'USER', '查询用户', 'QUERY_USER', 'QUERY', name='查询全部用户', method='GET', path='/usercenter/user/all')
    create_api('USERCENTER', 'USER', '修改用户', 'MODIFY_USER', 'MODIFY', name='修改用户信息', method='PUT', path='/usercenter/user')
    create_api('USERCENTER', 'USER', '修改用户', 'MODIFY_USER', 'MODIFY', name='修改用户状态', method='PATCH', path='/usercenter/user/state')
    create_api('USERCENTER', 'USER', '删除用户', 'REMOVE_USER', 'REMOVE', name='删除用户', method='DELETE', path='/usercenter/user')
    create_api('USERCENTER', 'ROLE', '查询用户', 'QUERY_ROLE', 'QUERY', name='查询用户全部角色', method='GET', path='/usercenter/user/role/all')
    # group
    create_api('USERCENTER', 'GROUP', '查询分组', 'QUERY_GROUP', 'QUERY', name='分页查询分组列表', method='GET', path='/usercenter/group/list')
    create_api('USERCENTER', 'GROUP', '查询分组', 'QUERY_GROUP', 'QUERY', name='查询全部分组', method='GET', path='/usercenter/group/all')
    create_api('USERCENTER', 'GROUP', '查询分组', 'QUERY_GROUP', 'QUERY', name='查询分组信息', method='GET', path='/usercenter/group/info')
    create_api('USERCENTER', 'GROUP', '新增分组', 'CREATE_GROUP', 'CREATE',  name='新增分组', method='POST', path='/usercenter/group')
    create_api('USERCENTER', 'GROUP', '修改分组', 'MODIFY_GROUP', 'MODIFY',  name='修改分组信息', method='PUT', path='/usercenter/group')
    create_api('USERCENTER', 'GROUP', '修改分组', 'MODIFY_GROUP', 'MODIFY',  name='修改分组状态', method='PATCH', path='/usercenter/group/state')
    create_api('USERCENTER', 'GROUP', '删除分组', 'REMOVE_GROUP', 'REMOVE',  name='删除分组', method='DELETE', path='/usercenter/group')
    # role
    create_api('USERCENTER', 'ROLE', '查询角色', 'QUERY_ROLE', 'QUERY', name='分页查询角色列表', method='GET', path='/usercenter/role/list')
    create_api('USERCENTER', 'ROLE', '查询角色', 'QUERY_ROLE', 'QUERY', name='查询全部角色', method='GET', path='/usercenter/role/all')
    create_api('USERCENTER', 'ROLE', '查询角色', 'QUERY_ROLE', 'QUERY', name='查询角色信息', method='GET', path='/usercenter/role/info')
    create_api('USERCENTER', 'ROLE', '新增角色', 'CREATE_ROLE', 'CREATE', name='新增角色', method='POST', path='/usercenter/role')
    create_api('USERCENTER', 'ROLE', '修改角色', 'MODIFY_ROLE', 'MODIFY', name='修改角色信息', method='PUT', path='/usercenter/role')
    create_api('USERCENTER', 'ROLE', '修改角色', 'MODIFY_ROLE', 'MODIFY', name='修改角色状态', method='PATCH', path='/usercenter/role/state')
    create_api('USERCENTER', 'ROLE', '删除角色', 'REMOVE_ROLE', 'REMOVE', name='删除角色', method='DELETE', path='/usercenter/role')
    create_api('USERCENTER', 'ROLE', '查询角色', 'QUERY_ROLE', 'QUERY', name='查询角色全部权限', method='GET', path='/usercenter/role/permissions')
    create_api('USERCENTER', 'ROLE', '修改角色', 'MODIFY_ROLE', 'MODIFY', name='设置角色权限', method='POST', path='/usercenter/role/permissions')
    # permission
    create_api('USERCENTER', 'PERMISSION', '查询权限', 'QUERY_PERMISSION', 'QUERY', name='查询全部权限', method='GET', path='/usercenter/permission/all')
    # log
    create_api('SYSTEM', 'LOG', '查询日志', 'QUERY_LOG', 'QUERY', name='分页查询操作日志列表', method='GET', path='/system/operation/log/list')
    # workspace
    create_api('PUBLIC', 'WORKSPACE', '查询空间', 'QUERY_WORKSPACE', 'QUERY', name='分页查询工作空间列表', method='GET', path='/public/workspace/list')
    create_api('PUBLIC', 'WORKSPACE', '查询空间', 'QUERY_WORKSPACE', 'QUERY', name='查询全部工作空间', method='GET', path='/public/workspace/all')
    create_api('PUBLIC', 'WORKSPACE', '查询空间', 'QUERY_WORKSPACE', 'QUERY', name='查询工作空间信息', method='GET', path='/public/workspace/info')
    create_api('PUBLIC', 'WORKSPACE', '新增空间', 'CREATE_WORKSPACE', 'CREATE', name='新增工作空间', method='POST', path='/public/workspace')
    create_api('PUBLIC', 'WORKSPACE', '修改空间', 'MODIFY_WORKSPACE', 'MODIFY', name='修改工作空间', method='PUT', path='/public/workspace')
    create_api('PUBLIC', 'WORKSPACE', '删除空间', 'REMOVE_WORKSPACE', 'REMOVE', name='删除工作空间', method='DELETE', path='/public/workspace')
    create_api('PUBLIC', 'WORKSPACE', '查询空间成员', 'QUERY_WORKSPACE_MEMBER', 'QUERY', name='分页查询空间成员列表', method='GET', path='/public/workspace/user/list')
    create_api('PUBLIC', 'WORKSPACE', '查询空间成员', 'QUERY_WORKSPACE_MEMBER', 'QUERY', name='查询全部空间成员', method='GET', path='/public/workspace/user/all')
    create_api('PUBLIC', 'WORKSPACE', '修改空间成员', 'MODIFY_WORKSPACE_MEMBER', 'MODIFY', name='修改空间成员', method='PUT', path='/public/workspace/user')
    create_api('PUBLIC', 'WORKSPACE', '查询空间限制', 'QUERY_WORKSPACE_RESTRICTION', 'QUERY', name='查询空间全部限制', method='GET', path='/public/workspace/restriction')
    create_api('PUBLIC', 'WORKSPACE', '设置空间限制', 'SET_WORKSPACE_RESTRICTION', 'SET', name='设置空间限制', method='POST', path='/public/workspace/restriction')
    # tag
    create_api('PUBLIC', 'TAG', '查询标签', 'QUERY_TAG', 'QUERY', name='分页查询标签列表', method='GET', path='/public/tag/list')
    create_api('PUBLIC', 'TAG', '查询标签', 'QUERY_TAG', 'QUERY', name='查询全部标签', method='GET', path='/public/tag/all')
    create_api('PUBLIC', 'TAG', '新增标签', 'CREATE_TAG', 'CREATE', name='新增标签', method='POST', path='/public/tag')
    create_api('PUBLIC', 'TAG', '修改标签', 'MODIFY_TAG', 'MODIFY', name='修改标签', method='PUT', path='/public/tag')
    create_api('PUBLIC', 'TAG', '删除标签', 'REMOVE_TAG', 'REMOVE', name='删除标签', method='DELETE', path='/public/tag')
    # message
    create_api('PUBLIC', 'MESSAGE', '查询机器人', 'QUERY_ROBOT', 'QUERY', name='分页查询通知机器人列表', method='GET', path='/public/notice/robot/list')
    create_api('PUBLIC', 'MESSAGE', '查询机器人', 'QUERY_ROBOT', 'QUERY', name='查询全部通知机器人', method='GET', path='/public/notice/robot/all')
    create_api('PUBLIC', 'MESSAGE', '查询机器人', 'QUERY_ROBOT', 'QUERY', name='查询通知机器人', method='GET', path='/public/notice/robot')
    create_api('PUBLIC', 'MESSAGE', '新增机器人', 'CREATE_ROBOT', 'CREATE', name='新增通知机器人', method='POST', path='/public/notice/robot')
    create_api('PUBLIC', 'MESSAGE', '修改机器人', 'MODIFY_ROBOT', 'MODIFY', name='修改通知机器人', method='PUT', path='/public/notice/robot')
    create_api('PUBLIC', 'MESSAGE', '修改机器人', 'MODIFY_ROBOT', 'MODIFY', name='修改通知机器人状态', method='PATCH', path='/public/notice/robot/state')
    create_api('PUBLIC', 'MESSAGE', '删除机器人', 'REMOVE_ROBOT', 'REMOVE', name='删除通知机器人', method='DELETE', path='/public/notice/robot')
    # task
    create_api('SCHEDULER', 'TASK', '查询定时任务', 'QUERY_TASK', 'QUERY', name='分页查询定时任务列表', method='GET', path='/schedule/task/list')
    create_api('SCHEDULER', 'TASK', '查询定时任务', 'QUERY_TASK', 'QUERY', name='查询定时任务信息', method='GET', path='/schedule/task/info')
    create_api('SCHEDULER', 'TASK', '新增定时任务', 'CREATE_TASK', 'CREATE', name='新增定时任务', method='POST', path='/schedule/task')
    create_api('SCHEDULER', 'TASK', '修改定时任务', 'MODIFY_TASK', 'MODIFY', name='修改定时任务', method='PUT', path='/schedule/task')
    create_api('SCHEDULER', 'TASK', '暂停定时任务', 'PAUSE_TASK', 'PAUSE', name='暂停定时任务', method='PATCH', path='/schedule/task/pause')
    create_api('SCHEDULER', 'TASK', '恢复定时任务', 'RESUME_TASK', 'RESUME', name='恢复定时任务', method='PATCH', path='/schedule/task/resume')
    create_api('SCHEDULER', 'TASK', '关闭定时任务', 'REMOVE_TASK', 'REMOVE', name='关闭定时任务', method='PATCH', path='/schedule/task/remove')
    create_api('SCHEDULER', 'TASK', '查询定时任务', 'QUERY_TASK', 'QUERY', name='分业查询任务历史列表', method='GET', path='/schedule/task/history/list')
    # job
    create_api('SCHEDULER', 'JOB', '查询定时作业', 'QUERY_JOB', 'QUERY', name='查询作业信息', method='GET', path='/schedule/job/info')
    create_api('SCHEDULER', 'JOB', '运行定时作业', 'RUN_JOB', 'EXECUTE', name='立即运行作业', method='POST', path='/schedule/job/run')
    # element
    create_api('SCRIPT', 'ELEMENT', '查询元素', 'QUERY_ELEMENT', 'QUERY', name='分页查询元素列表', method='GET', path='/script/element/list')
    create_api('SCRIPT', 'ELEMENT', '查询元素', 'QUERY_ELEMENT', 'QUERY', name='查询全部元素', method='GET', path='/script/element/all')
    create_api('SCRIPT', 'ELEMENT', '查询元素', 'QUERY_ELEMENT', 'QUERY', name='查询用户空间下的所有元素（用于私人空间）', method='GET', path='/script/element/all/in/private')
    create_api('SCRIPT', 'ELEMENT', '查询元素', 'QUERY_ELEMENT', 'QUERY', name='查询全部元素及其子代', method='GET', path='/script/element/all/with/children')
    create_api('SCRIPT', 'ELEMENT', '查询元素', 'QUERY_ELEMENT', 'QUERY', name='查询元素信息', method='GET', path='/script/element/info')
    create_api('SCRIPT', 'ELEMENT', '查询元素', 'QUERY_ELEMENT', 'QUERY', name='查询元素子代', method='GET', path='/script/element/children')
    create_api('SCRIPT', 'ELEMENT', '查询元素', 'QUERY_ELEMENT', 'QUERY', name='根据编号列表批量查询子代元素', method='GET', path='/script/elements/children')
    create_api('SCRIPT', 'ELEMENT', '新增元素', 'CREATE_ELEMENT', 'CREATE', name='新增集合元素', method='POST', path='/script/collection')
    create_api('SCRIPT', 'ELEMENT', '新增元素', 'CREATE_ELEMENT', 'CREATE', name='新增子代元素', method='POST', path='/script/element/child')
    create_api('SCRIPT', 'ELEMENT', '新增元素', 'CREATE_ELEMENT', 'CREATE', name='根据列表新增子代元素', method='POST', path='/script/element/children')
    create_api('SCRIPT', 'ELEMENT', '新增元素', 'CREATE_ELEMENT', 'CREATE', name='新增HTTP取样器', method='POST', path='/script/element/http/sampler')
    create_api('SCRIPT', 'ELEMENT', '修改元素', 'MODIFY_ELEMENT', 'MODIFY', name='修改HTTP取样器', method='PUT', path='/script/element/http/sampler')
    create_api('SCRIPT', 'ELEMENT', '修改元素', 'MODIFY_ELEMENT', 'MODIFY', name='修改元素', method='PUT', path='/script/element')
    create_api('SCRIPT', 'ELEMENT', '删除元素', 'REMOVE_ELEMENT', 'REMOVE', name='删除元素', method='DELETE', path='/script/element')
    create_api('SCRIPT', 'ELEMENT', '修改元素', 'MODIFY_ELEMENT', 'MODIFY', name='启用元素', method='PATCH', path='/script/element/enable')
    create_api('SCRIPT', 'ELEMENT', '修改元素', 'MODIFY_ELEMENT', 'MODIFY', name='禁用元素', method='PATCH', path='/script/element/disable')
    create_api('SCRIPT', 'ELEMENT', '修改元素', 'MODIFY_ELEMENT', 'MODIFY', name='切换元素状态', method='PATCH', path='/script/element/state/toggle')
    create_api('SCRIPT', 'ELEMENT', '移动元素', 'MOVE_ELEMENT', 'MOVE', name='移动元素', method='POST', path='/script/element/move')
    create_api('SCRIPT', 'ELEMENT', '复制元素', 'COPY_ELEMENT', 'COPY', name='复制元素及其子代', method='POST', path='/script/element/duplicate')
    create_api('SCRIPT', 'ELEMENT', '查询元素', 'QUERY_ELEMENT', 'QUERY', name='查询HTTP请求头引用', method='GET', path='/script/element/httpheader/template/refs')
    create_api('SCRIPT', 'ELEMENT', '新增元素', 'CREATE_ELEMENT', 'CREATE', name='新增HTTP请求头引用', method='POST', path='/script/element/httpheader/template/refs')
    create_api('SCRIPT', 'ELEMENT', '修改元素', 'MODIFY_ELEMENT', 'MODIFY', name='修改HTTP请求头引用', method='PUT', path='/script/element/httpheader/template/refs')
    create_api('SCRIPT', 'ELEMENT', '查询元素', 'QUERY_ELEMENT', 'QUERY', name='查询内置元素', method='GET', path='/script/element/builtins')
    create_api('SCRIPT', 'ELEMENT', '新增元素', 'CREATE_ELEMENT', 'CREATE', name='新增内置元素', method='POST', path='/script/element/builtins')
    create_api('SCRIPT', 'ELEMENT', '修改元素', 'MODIFY_ELEMENT', 'MODIFY', name='修改内置元素', method='PUT', path='/script/element/builtins')
    create_api('SCRIPT', 'ELEMENT', '移动元素', 'MOVE_ELEMENT', 'MOVE', name='剪贴元素', method='POST', path='/script/element/paste')
    create_api('SCRIPT', 'ELEMENT', '复制元素', 'COPY_ELEMENT', 'COPY', name='复制集合到指定空间', method='POST', path='/script/element/collection/copy/to/workspace')
    create_api('SCRIPT', 'ELEMENT', '移动元素', 'MOVE_ELEMENT', 'MOVE', name='移动集合到指定空间', method='POST', path='/script/element/collection/move/to/workspace')
    create_api('SCRIPT', 'ELEMENT', '查询空间组件', 'QUERY_WORKSPACE_COMPONENT', 'QUERY', name='根据空间查询全部组件', method='GET', path='/script/element/workspace/components')
    create_api('SCRIPT', 'ELEMENT', '设置空间组件', 'SET_WORKSPACE_COMPONENT', 'SET', name='设置空间组件', method='POST', path='/script/element/workspace/components')
    # execution
    create_api('SCRIPT', 'ELEMENT', '运行脚本', 'RUN_ELEMENT', 'EXECUTE', name='运行测试集合', method='POST', path='/script/collection/execute')
    create_api('SCRIPT', 'ELEMENT', '运行脚本', 'RUN_ELEMENT', 'EXECUTE', name='运行测试案例', method='POST', path='/script/group/execute')
    create_api('SCRIPT', 'ELEMENT', '运行脚本', 'RUN_ELEMENT', 'EXECUTE', name='运行取样器', method='POST', path='/script/sampler/execute')
    create_api('SCRIPT', 'ELEMENT', '运行脚本', 'RUN_ELEMENT', 'EXECUTE', name='运行片段集合', method='POST', path='/script/snippets/execute')
    create_api('SCRIPT', 'ELEMENT', '查询JSON脚本', 'QUERY_JSON_SCRIPT', 'QUERY', name='查询测试集合的JSON脚本', method='GET', path='/script/collection/json')
    create_api('SCRIPT', 'ELEMENT', '查询JSON脚本', 'QUERY_JSON_SCRIPT', 'QUERY', name='查询测试案例的JSON脚本', method='GET', path='/script/group/json')
    create_api('SCRIPT', 'ELEMENT', '查询JSON脚本', 'QUERY_JSON_SCRIPT', 'QUERY', name='查询片段集合的JSON脚本', method='GET', path='/script/snippets/json')
    # variables
    create_api('SCRIPT', 'VARIABLE', '查询变量集', 'QUERY_DATASET', 'QUERY', name='分页查询变量集列表', method='GET', path='/script/variable/dataset/list')
    create_api('SCRIPT', 'VARIABLE', '查询变量集', 'QUERY_DATASET', 'QUERY', name='查询全部变量集', method='GET', path='/script/variable/dataset/all')
    create_api('SCRIPT', 'VARIABLE', '查询变量集', 'QUERY_DATASET', 'QUERY', name='根据用户空间查询全部变量集', method='GET', path='/script/variable/dataset/all/in/private')
    create_api('SCRIPT', 'VARIABLE', '新增变量集', 'CREATE_DATASET', 'CREATE', name='新增变量集', method='POST', path='/script/variable/dataset')
    create_api('SCRIPT', 'VARIABLE', '修改变量集', 'MODIFY_DATASET', 'MODIFY', name='修改变量集', method='PUT', path='/script/variable/dataset')
    create_api('SCRIPT', 'VARIABLE', '删除变量集', 'REMOVE_DATASET', 'REMOVE', name='删除变量集', method='DELETE', path='/script/variable/dataset')
    create_api('SCRIPT', 'VARIABLE', '复制变量集', 'COPY_VARIABLE', 'COPY', name='复制变量集到指定工作空间', method='POST', path='/script/variable/dataset/copy/to/workspace')
    create_api('SCRIPT', 'VARIABLE', '移动变量集', 'MOVE_VARIABLE', 'MOVE', name='移动变量集到指定工作空间', method='POST', path='/script/variable/dataset/move/to/workspace')
    create_api('SCRIPT', 'VARIABLE', '新增变量', 'CREATE_VARIABLE', 'CREATE', name='新增变量', method='POST', path='/script/variable')
    create_api('SCRIPT', 'VARIABLE', '修改变量', 'MODIFY_VARIABLE', 'MODIFY', name='修改变量', method='PUT', path='/script/variable')
    create_api('SCRIPT', 'VARIABLE', '删除变量', 'REMOVE_VARIABLE', 'REMOVE', name='删除变量', method='DELETE', path='/script/variable')
    create_api('SCRIPT', 'VARIABLE', '修改变量', 'MODIFY_VARIABLE', 'MODIFY', name='启用变量', method='PATCH', path='/script/variable/enable')
    create_api('SCRIPT', 'VARIABLE', '修改变量', 'MODIFY_VARIABLE', 'MODIFY', name='禁用变量', method='PATCH', path='/script/variable/disable')
    create_api('SCRIPT', 'VARIABLE', '修改变量', 'MODIFY_VARIABLE', 'MODIFY', name='更新变量当前值', method='PATCH', path='/script/variable/current/value')
    create_api('SCRIPT', 'VARIABLE', '查询变量', 'QUERY_VARIABLE', 'QUERY', name='根据集合查询全部变量', method='GET', path='/script/variables/by/dataset')
    create_api('SCRIPT', 'VARIABLE', '查询变量', 'QUERY_VARIABLE', 'QUERY', name='根据列表批量查询变量', method='GET', path='/script/variables')
    create_api('SCRIPT', 'VARIABLE', '新增变量', 'CREATE_VARIABLE', 'CREATE', name='根据列表批量新增变量', method='POST', path='/script/variables')
    create_api('SCRIPT', 'VARIABLE', '修改变量', 'MODIFY_VARIABLE', 'MODIFY', name='根据列表批量修改变量', method='PUT', path='/script/variables')
    create_api('SCRIPT', 'VARIABLE', '删除变量', 'REMOVE_VARIABLE', 'REMOVE', name='根据列表批量删除变量', method='DELETE', path='/script/variables')
    create_api('SCRIPT', 'VARIABLE', '复制变量', 'COPY_VARIABLE', 'COPY', name='复制变量集', method='POST', path='/script/variable/dataset/duplicate')
    # headers
    create_api('SCRIPT', 'HTTP_HEADER', '查询HTTP请求头模板', 'QUERY_HTTPHEADER_TEMPLATE', 'QUERY', name='分页查询请求头模板列表', method='GET', path='/script/httpheader/template/list')
    create_api('SCRIPT', 'HTTP_HEADER', '查询HTTP请求头模板', 'QUERY_HTTPHEADER_TEMPLATE', 'QUERY', name='查询全部请求头模板', method='GET', path='/script/httpheader/template/all')
    create_api('SCRIPT', 'HTTP_HEADER', '查询HTTP请求头模板', 'QUERY_HTTPHEADER_TEMPLATE', 'QUERY', name='根据用户空间查询全部请求头模板', method='GET', path='/script/httpheader/template/all/in/private')
    create_api('SCRIPT', 'HTTP_HEADER', '新增HTTP请求头模板', 'CREATE_HTTPHEADER_TEMPLATE', 'CREATE', name='新增请求头模板', method='POST', path='/script/httpheader/template')
    create_api('SCRIPT', 'HTTP_HEADER', '修改HTTP请求头模板', 'MODIFY_HTTPHEADER_TEMPLATE', 'MODIFY', name='修改请求头模板', method='PUT', path='/script/httpheader/template')
    create_api('SCRIPT', 'HTTP_HEADER', '删除HTTP请求头模板', 'REMOVE_HTTPHEADER_TEMPLATE', 'REMOVE', name='删除请求头模板', method='DELETE', path='/script/httpheader/template')
    create_api('SCRIPT', 'HTTP_HEADER', '复制HTTP请求头模板', 'COPY_HTTPHEADER_TEMPLATE', 'COPY', name='复制请求头模板', method='POST', path='/script/httpheader/template/duplicate')
    create_api('SCRIPT', 'HTTP_HEADER', '复制HTTP请求头模板', 'COPY_HTTPHEADER_TEMPLATE', 'COPY', name='复制请求头模板到指定工作空间', method='POST', path='/script/httpheader/template/copy/to/workspace')
    create_api('SCRIPT', 'HTTP_HEADER', '移动HTTP请求头模板', 'MOVE_HTTPHEADER_TEMPLATE', 'MOVE', name='移动请求头模板到指定工作空间', method='POST', path='/script/httpheader/template/move/to/workspace')
    create_api('SCRIPT', 'HTTP_HEADER', '新增HTTP请求头', 'CREATE_HTTP_HEADER', 'CREATE', name='新增请求头', method='POST', path='/script/http/header')
    create_api('SCRIPT', 'HTTP_HEADER', '修改HTTP请求头', 'MODIFY_HTTP_HEADER', 'MODIFY', name='修改请求头', method='PUT', path='/script/http/header')
    create_api('SCRIPT', 'HTTP_HEADER', '删除HTTP请求头', 'REMOVE_HTTP_HEADER', 'REMOVE', name='删除请求头', method='DELETE', path='/script/http/header')
    create_api('SCRIPT', 'HTTP_HEADER', '修改HTTP请求头', 'MODIFY_HTTP_HEADER', 'MODIFY', name='启用请求头', method='PATCH', path='/script/http/header/enable')
    create_api('SCRIPT', 'HTTP_HEADER', '修改HTTP请求头', 'MODIFY_HTTP_HEADER', 'MODIFY', name='禁用请求头', method='PATCH', path='/script/http/header/disable')
    create_api('SCRIPT', 'HTTP_HEADER', '查询HTTP请求头', 'QUERY_HTTP_HEADER', 'QUERY', name='根据模板查询全部请求头', method='GET', path='/script/http/headers/by/template')
    create_api('SCRIPT', 'HTTP_HEADER', '查询HTTP请求头', 'QUERY_HTTP_HEADER', 'QUERY', name='根据列表批量查询请求头', method='GET', path='/script/http/headers')
    create_api('SCRIPT', 'HTTP_HEADER', '新增HTTP请求头', 'CREATE_HTTP_HEADER', 'CREATE', name='根据列表批量新增请求头', method='POST', path='/script/http/headers')
    create_api('SCRIPT', 'HTTP_HEADER', '修改HTTP请求头', 'MODIFY_HTTP_HEADER', 'MODIFY', name='根据列表批量修改请求头', method='PUT', path='/script/http/headers')
    create_api('SCRIPT', 'HTTP_HEADER', '删除HTTP请求头', 'REMOVE_HTTP_HEADER', 'REMOVE', name='根据列表批量删除请求头', method='DELETE', path='/script/http/headers')
    # database
    create_api('SCRIPT', 'DATABASE', '查询数据库配置', 'QUERY_DATABASE_ENGINE', 'QUERY', name='分页查询数据库配置列表', method='GET', path='/script/database/engine/list')
    create_api('SCRIPT', 'DATABASE', '查询数据库配置', 'QUERY_DATABASE_ENGINE', 'QUERY', name='查询全部数据库配置', method='GET', path='/script/database/engine/all')
    create_api('SCRIPT', 'DATABASE', '查询数据库配置', 'QUERY_DATABASE_ENGINE', 'QUERY', name='根据用户空间查询全部数据库配置', method='GET', path='/script/database/engine/all/in/private')
    create_api('SCRIPT', 'DATABASE', '查询数据库配置', 'QUERY_DATABASE_ENGINE', 'QUERY', name='查询数据库配置', method='GET', path='/script/database/engine')
    create_api('SCRIPT', 'DATABASE', '新增数据库配置', 'CREATE_DATABASE_ENGINE', 'CREATE', name='新增数据库配置', method='POST', path='/script/database/engine')
    create_api('SCRIPT', 'DATABASE', '修改数据库配置', 'MODIFY_DATABASE_ENGINE', 'MODIFY', name='修改数据库配置', method='PUT', path='/script/database/engine')
    create_api('SCRIPT', 'DATABASE', '删除数据库配置', 'REMOVE_DATABASE_ENGINE', 'REMOVE', name='删除数据库配置', method='DELETE', path='/script/database/engine')
    create_api('SCRIPT', 'DATABASE', '复制数据库配置', 'COPY_DATABASE_ENGINE', 'COPY', name='复制数据库配置', method='POST', path='/script/database/engine/duplicate')
    create_api('SCRIPT', 'DATABASE', '复制数据库配置', 'COPY_DATABASE_ENGINE', 'COPY', name='复制数据库配置到指定工作空间', method='POST', path='/script/database/engine/copy/to/workspace')
    create_api('SCRIPT', 'DATABASE', '移动数据库配置', 'MOVE_DATABASE_ENGINE', 'MOVE', name='移动数据库配置到指定工作空间', method='POST', path='/script/database/engine/move/to/workspace')
    # testplan
    create_api('SCRIPT', 'TESTPLAN', '查询测试计划', 'QUERY_TESTPLAN', 'QUERY', name='分页查询测试计划列表', method='GET', path='/script/testplan/list')
    create_api('SCRIPT', 'TESTPLAN', '查询测试计划', 'QUERY_TESTPLAN', 'QUERY', name='查询全部测试计划', method='GET', path='/script/testplan/all')
    create_api('SCRIPT', 'TESTPLAN', '查询测试计划', 'QUERY_TESTPLAN', 'QUERY', name='查询测试计划详情', method='GET', path='/script/testplan')
    create_api('SCRIPT', 'TESTPLAN', '新增测试计划', 'CREATE_TESTPLAN', 'CREATE', name='新增测试计划', method='POST', path='/script/testplan')
    create_api('SCRIPT', 'TESTPLAN', '修改测试计划', 'MODIFY_TESTPLAN', 'MODIFY', name='修改测试计划', method='PUT', path='/script/testplan')
    create_api('SCRIPT', 'TESTPLAN', '修改测试计划', 'MODIFY_TESTPLAN', 'MODIFY', name='修改测试计划状态', method='PATCH', path='/script/testplan/state')
    create_api('SCRIPT', 'TESTPLAN', '修改测试计划', 'MODIFY_TESTPLAN', 'MODIFY', name='修改测试计划测试阶段', method='PATCH', path='/script/testplan/testphase')
    create_api('SCRIPT', 'TESTPLAN', '运行测试计划', 'RUN_TESTPLAN', 'EXECUTE', name='运行测试计划', method='POST', path='/script/testplan/execute')
    create_api('SCRIPT', 'TESTPLAN', '中断测试计划', 'INTERRUPT_TESTPLAN', 'INTERRUPT', name='中断运行测试计划', method='POST', path='/script/testplan/execution/interrupt')
    create_api('SCRIPT', 'TESTPLAN', '查询执行记录', 'QUERY_TESTPLAN_EXECUTION', 'QUERY', name='查询全部执行记录', method='GET', path='/script/testplan/execution/all')
    create_api('SCRIPT', 'TESTPLAN', '查询执行记录', 'QUERY_TESTPLAN_EXECUTION', 'QUERY', name='查询执行记录详情', method='GET', path='/script/testplan/execution/details')
    # testreport
    create_api('SCRIPT', 'TESTREPORT', '查询测试报告', 'QUERY_TESTREPORT', 'QUERY', name='查询测试报告', method='GET', path='/script/report')
    create_api('SCRIPT', 'TESTREPORT', '查询测试报告', 'QUERY_TESTREPORT', 'QUERY', name='根据集合编号查询集合结果列表和案例结果列表', method='GET', path='/script/report/collection/result')
    create_api('SCRIPT', 'TESTREPORT', '查询测试报告', 'QUERY_TESTREPORT', 'QUERY', name='根据案例编号查询案例结果列表', method='GET', path='/script/report/group/result')
    create_api('SCRIPT', 'TESTREPORT', '查询测试报告', 'QUERY_TESTREPORT', 'QUERY', name='根据取样器编号查询取样结果', method='GET', path='/script/report/sampler/result')

    click.echo('创建权限接口成功')


@with_appcontext
def init_user_role():
    """初始化用户角色关联"""
    user = TUser.filter_by(USER_NAME='超级管理员').first()
    role = TRole.filter_by(ROLE_NAME='超级管理员', ROLE_CODE='SUPER_ADMIN').first()
    TUserRole.insert_without_record(USER_NO=user.USER_NO, ROLE_NO=role.ROLE_NO)
    click.echo('创建用户角色关联成功')


@with_appcontext
def init_global_variable_dataset():
    TVariableDataset.insert_without_record(DATASET_NO=new_id(), DATASET_NAME='public', DATASET_TYPE='GLOBAL', WEIGHT=1)
    click.echo('初始化PyMeter全局变量成功')


def create_role(name, code, rank):
    TRole.insert_without_record(ROLE_NO=new_id(), ROLE_NAME=name, ROLE_CODE=code, ROLE_RANK=rank, ROLE_TYPE='SYSTEM')


def create_api(m_code, o_code, p_name, p_code, p_act, name, method, path):
    api_no = new_id()
    TApi.insert_without_record(
        API_NO=api_no,
        API_NAME=name,
        API_TYPE='HTTP',
        HTTP_METHOD=method,
        HTTP_PATH=path
    )
    TPermissionApi.insert_without_record(
        PERMISSION_NO=get_permission_no(m_code, o_code, p_name, p_code, p_act),
        API_NO=api_no
    )


def get_permission_no(module_code, object_code, permission_name, permission_code, permission_act):
    if permission := TPermission.filter(
            TPermissionModule.MODULE_CODE == module_code,
            TPermissionObject.OBJECT_CODE == object_code,
            TPermission.PERMISSION_CODE == permission_code,
            TPermission.PERMISSION_ACT == permission_act,
            TPermission.MODULE_NO == TPermissionModule.MODULE_NO,
            TPermission.OBJECT_NO == TPermissionObject.OBJECT_NO
    ).first():
        return permission.PERMISSION_NO

    permission_no = new_id()
    TPermission.insert_without_record(
        MODULE_NO=get_permission_module_no(module_code),
        OBJECT_NO=get_permission_object_no(object_code),
        PERMISSION_NO=permission_no,
        PERMISSION_NAME=permission_name,
        PERMISSION_CODE=permission_code,
        PERMISSION_ACT=permission_act
    )
    return permission_no


def get_permission_module_no(code):
    return TPermissionModule.filter_by(MODULE_CODE=code).first().MODULE_NO


def get_permission_object_no(code):
    return TPermissionObject.filter_by(OBJECT_CODE=code).first().OBJECT_NO


@click.command('create-table')
@click.option('-n', '--name', help='表名')
@with_appcontext
def create_table(name):
    from sqlalchemy import create_engine

    from app import config as CONFIG
    from app.public import model as public_model
    from app.schedule import model as schedule_model
    from app.script import model as script_model
    from app.system import model as system_model
    from app.usercenter import model as usercenter_model

    engine = create_engine(CONFIG.DB_URL)

    if hasattr(public_model, name):
        table = getattr(public_model, name)
    elif hasattr(schedule_model, name):
        table = getattr(schedule_model, name)
    elif hasattr(script_model, name):
        table = getattr(script_model, name)
    elif hasattr(system_model, name):
        table = getattr(system_model, name)
    elif hasattr(usercenter_model, name):
        table = getattr(usercenter_model, name)
    else:
        table = None

    if table:
        table.__table__.create(engine, checkfirst=True)
        click.echo('新增表格成功')
    else:
        click.echo('表格名称不存在')
        return
