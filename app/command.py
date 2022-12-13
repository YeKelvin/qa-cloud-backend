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
        WORKSPACE_NAME='个人空间',
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
    init_permission_item()
    click.echo('创建权限成功')


@with_appcontext
def init_permission_module():
    TPermissionModule.insert_without_record(MODULE_NO=new_id(), MODULE_NAME='用户中心', MODULE_CODE='USERCENTER')
    TPermissionModule.insert_without_record(MODULE_NO=new_id(), MODULE_NAME='系统', MODULE_CODE='SYSTEM')
    TPermissionModule.insert_without_record(MODULE_NO=new_id(), MODULE_NAME='公共', MODULE_CODE='PUBLIC')
    TPermissionModule.insert_without_record(MODULE_NO=new_id(), MODULE_NAME='脚本', MODULE_CODE='SCRIPT')
    TPermissionModule.insert_without_record(MODULE_NO=new_id(), MODULE_NAME='调度', MODULE_CODE='SCHEDULER')


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


@with_appcontext
def init_permission_item():
    """初始化接口"""
    """
    # 遍历所有接口
    import flask
    app = flask.current_app._get_current_object()
    for rule in app.url_map.iter_rules():
        print(rule)
    """
    # user
    create_permission('USERCENTER', 'USER', '用户注册', 'REGISTER', 'CREATE')
    create_permission('USERCENTER', 'USER', '重置密码', 'RESET_PASSWORD', 'MODIFY')
    create_permission('USERCENTER', 'USER', '查询用户', 'QUERY_USER', 'QUERY')
    create_permission('USERCENTER', 'USER', '修改用户', 'MODIFY_USER', 'MODIFY')
    create_permission('USERCENTER', 'USER', '删除用户', 'REMOVE_USER', 'REMOVE')
    # group
    create_permission('USERCENTER', 'GROUP', '查询分组', 'QUERY_GROUP', 'QUERY')
    create_permission('USERCENTER', 'GROUP', '新增分组', 'CREATE_GROUP', 'CREATE')
    create_permission('USERCENTER', 'GROUP', '修改分组', 'MODIFY_GROUP', 'MODIFY')
    create_permission('USERCENTER', 'GROUP', '删除分组', 'REMOVE_GROUP', 'REMOVE')
    # role
    create_permission('USERCENTER', 'ROLE', '查询角色', 'QUERY_ROLE', 'QUERY')
    create_permission('USERCENTER', 'ROLE', '新增角色', 'CREATE_ROLE', 'CREATE')
    create_permission('USERCENTER', 'ROLE', '修改角色', 'MODIFY_ROLE', 'MODIFY')
    create_permission('USERCENTER', 'ROLE', '删除角色', 'REMOVE_ROLE', 'REMOVE')
    # permission
    create_permission('USERCENTER', 'PERMISSION', '查询权限', 'QUERY_PERMISSION', 'QUERY')
    # log
    create_permission('SYSTEM', 'LOG', '查询日志', 'QUERY_LOG', 'QUERY')
    # workspace
    create_permission('PUBLIC', 'WORKSPACE', '查询空间', 'QUERY_WORKSPACE', 'QUERY')
    create_permission('PUBLIC', 'WORKSPACE', '新增空间', 'CREATE_WORKSPACE', 'CREATE')
    create_permission('PUBLIC', 'WORKSPACE', '修改空间', 'MODIFY_WORKSPACE', 'MODIFY')
    create_permission('PUBLIC', 'WORKSPACE', '删除空间', 'REMOVE_WORKSPACE', 'REMOVE')
    create_permission('PUBLIC', 'WORKSPACE', '查询空间成员', 'QUERY_WORKSPACE_MEMBER', 'QUERY')
    create_permission('PUBLIC', 'WORKSPACE', '修改空间成员', 'MODIFY_WORKSPACE_MEMBER', 'MODIFY')
    create_permission('PUBLIC', 'WORKSPACE', '查询空间限制', 'QUERY_WORKSPACE_RESTRICTION', 'QUERY')
    create_permission('PUBLIC', 'WORKSPACE', '设置空间限制', 'SET_WORKSPACE_RESTRICTION', 'SET')
    # tag
    create_permission('PUBLIC', 'TAG', '查询标签', 'QUERY_TAG', 'QUERY')
    create_permission('PUBLIC', 'TAG', '新增标签', 'CREATE_TAG', 'CREATE')
    create_permission('PUBLIC', 'TAG', '修改标签', 'MODIFY_TAG', 'MODIFY')
    create_permission('PUBLIC', 'TAG', '删除标签', 'REMOVE_TAG', 'REMOVE')
    # message
    create_permission('PUBLIC', 'MESSAGE', '查询机器人', 'QUERY_ROBOT', 'QUERY')
    create_permission('PUBLIC', 'MESSAGE', '新增机器人', 'CREATE_ROBOT', 'CREATE')
    create_permission('PUBLIC', 'MESSAGE', '修改机器人', 'MODIFY_ROBOT', 'MODIFY')
    create_permission('PUBLIC', 'MESSAGE', '删除机器人', 'REMOVE_ROBOT', 'REMOVE')
    # task
    create_permission('SCHEDULER', 'TASK', '查询定时任务', 'QUERY_TASK', 'QUERY')
    create_permission('SCHEDULER', 'TASK', '新增定时任务', 'CREATE_TASK', 'CREATE')
    create_permission('SCHEDULER', 'TASK', '修改定时任务', 'MODIFY_TASK', 'MODIFY')
    create_permission('SCHEDULER', 'TASK', '暂停定时任务', 'PAUSE_TASK', 'PAUSE')
    create_permission('SCHEDULER', 'TASK', '恢复定时任务', 'RESUME_TASK', 'RESUME')
    create_permission('SCHEDULER', 'TASK', '关闭定时任务', 'REMOVE_TASK', 'REMOVE')
    # job
    create_permission('SCHEDULER', 'JOB', '查询定时作业', 'QUERY_JOB', 'QUERY')
    create_permission('SCHEDULER', 'JOB', '运行定时作业', 'RUN_JOB', 'EXECUTE')
    # element
    create_permission('SCRIPT', 'ELEMENT', '查询元素', 'QUERY_ELEMENT', 'QUERY')
    create_permission('SCRIPT', 'ELEMENT', '新增元素', 'CREATE_ELEMENT', 'CREATE')
    create_permission('SCRIPT', 'ELEMENT', '修改元素', 'MODIFY_ELEMENT', 'MODIFY')
    create_permission('SCRIPT', 'ELEMENT', '删除元素', 'REMOVE_ELEMENT', 'REMOVE')
    create_permission('SCRIPT', 'ELEMENT', '移动元素', 'MOVE_ELEMENT', 'MOVE')
    create_permission('SCRIPT', 'ELEMENT', '复制元素', 'COPY_ELEMENT', 'COPY')
    create_permission('SCRIPT', 'ELEMENT', '剪贴元素', 'PASTE_ELEMENT', 'PASTE')
    create_permission('SCRIPT', 'ELEMENT', '查询空间组件', 'QUERY_WORKSPACE_COMPONENT', 'QUERY')
    create_permission('SCRIPT', 'ELEMENT', '设置空间组件', 'SET_WORKSPACE_COMPONENT', 'SET')
    # execution
    create_permission('SCRIPT', 'ELEMENT', '运行脚本', 'RUN_ELEMENT', 'EXECUTE')
    create_permission('SCRIPT', 'ELEMENT', '查询JSON脚本', 'QUERY_JSON_SCRIPT', 'QUERY')
    # variables
    create_permission('SCRIPT', 'VARIABLE', '查询变量集', 'QUERY_DATASET', 'QUERY')
    create_permission('SCRIPT', 'VARIABLE', '新增变量集', 'CREATE_DATASET', 'CREATE')
    create_permission('SCRIPT', 'VARIABLE', '修改变量集', 'MODIFY_DATASET', 'MODIFY')
    create_permission('SCRIPT', 'VARIABLE', '删除变量集', 'REMOVE_DATASET', 'REMOVE')
    create_permission('SCRIPT', 'VARIABLE', '复制变量集', 'COPY_DATASET', 'COPY')
    create_permission('SCRIPT', 'VARIABLE', '移动变量集', 'MOVE_DATASET', 'MOVE')
    create_permission('SCRIPT', 'VARIABLE', '查询变量', 'QUERY_VARIABLE', 'QUERY')
    create_permission('SCRIPT', 'VARIABLE', '新增变量', 'CREATE_VARIABLE', 'CREATE')
    create_permission('SCRIPT', 'VARIABLE', '修改变量', 'MODIFY_VARIABLE', 'MODIFY')
    create_permission('SCRIPT', 'VARIABLE', '删除变量', 'REMOVE_VARIABLE', 'REMOVE')
    # headers
    create_permission('SCRIPT', 'HTTP_HEADER', '查询HTTP请求头模板', 'QUERY_HTTPHEADER_TEMPLATE', 'QUERY')
    create_permission('SCRIPT', 'HTTP_HEADER', '新增HTTP请求头模板', 'CREATE_HTTPHEADER_TEMPLATE', 'CREATE')
    create_permission('SCRIPT', 'HTTP_HEADER', '修改HTTP请求头模板', 'MODIFY_HTTPHEADER_TEMPLATE', 'MODIFY')
    create_permission('SCRIPT', 'HTTP_HEADER', '删除HTTP请求头模板', 'REMOVE_HTTPHEADER_TEMPLATE', 'REMOVE')
    create_permission('SCRIPT', 'HTTP_HEADER', '复制HTTP请求头模板', 'COPY_HTTPHEADER_TEMPLATE', 'COPY')
    create_permission('SCRIPT', 'HTTP_HEADER', '移动HTTP请求头模板', 'MOVE_HTTPHEADER_TEMPLATE', 'MOVE')
    create_permission('SCRIPT', 'HTTP_HEADER', '查询HTTP请求头', 'QUERY_HTTP_HEADER', 'QUERY')
    create_permission('SCRIPT', 'HTTP_HEADER', '新增HTTP请求头', 'CREATE_HTTP_HEADER', 'CREATE')
    create_permission('SCRIPT', 'HTTP_HEADER', '修改HTTP请求头', 'MODIFY_HTTP_HEADER', 'MODIFY')
    create_permission('SCRIPT', 'HTTP_HEADER', '删除HTTP请求头', 'REMOVE_HTTP_HEADER', 'REMOVE')
    # database
    create_permission('SCRIPT', 'DATABASE', '查询数据库配置', 'QUERY_DATABASE_ENGINE', 'QUERY')
    create_permission('SCRIPT', 'DATABASE', '新增数据库配置', 'CREATE_DATABASE_ENGINE', 'CREATE')
    create_permission('SCRIPT', 'DATABASE', '修改数据库配置', 'MODIFY_DATABASE_ENGINE', 'MODIFY')
    create_permission('SCRIPT', 'DATABASE', '删除数据库配置', 'REMOVE_DATABASE_ENGINE', 'REMOVE')
    create_permission('SCRIPT', 'DATABASE', '复制数据库配置', 'COPY_DATABASE_ENGINE', 'COPY')
    create_permission('SCRIPT', 'DATABASE', '移动数据库配置', 'MOVE_DATABASE_ENGINE', 'MOVE')
    # testplan
    create_permission('SCRIPT', 'TESTPLAN', '查询测试计划', 'QUERY_TESTPLAN', 'QUERY')
    create_permission('SCRIPT', 'TESTPLAN', '新增测试计划', 'CREATE_TESTPLAN', 'CREATE')
    create_permission('SCRIPT', 'TESTPLAN', '修改测试计划', 'MODIFY_TESTPLAN', 'MODIFY')
    create_permission('SCRIPT', 'TESTPLAN', '运行测试计划', 'RUN_TESTPLAN', 'EXECUTE')
    create_permission('SCRIPT', 'TESTPLAN', '中断测试计划', 'INTERRUPT_TESTPLAN', 'INTERRUPT')
    create_permission('SCRIPT', 'TESTPLAN', '查询执行记录', 'QUERY_TESTPLAN_EXECUTION', 'QUERY')
    # testreport
    create_permission('SCRIPT', 'TESTREPORT', '查询测试报告', 'QUERY_TESTREPORT', 'QUERY')


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


def create_permission(module_code, object_code, name, code, act):
    permission_no = new_id()
    TPermission.insert_without_record(
        MODULE_NO=get_permission_module_no(module_code),
        OBJECT_NO=get_permission_object_no(object_code),
        PERMISSION_NO=permission_no,
        PERMISSION_NAME=name,
        PERMISSION_CODE=code,
        PERMISSION_ACT=act
    )


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
