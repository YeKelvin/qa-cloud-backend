#!/usr/bin/ python3
# @File    : command.py
# @Time    : 2019/11/7 10:55
# @Author  : Kelvin.Ye
import click

from flask.cli import with_appcontext

from app.extension import db  # noqa
from app.modules.public.model import TWorkspace  # noqa
from app.modules.public.model import TWorkspaceUser  # noqa
from app.modules.script.model import TTestElement  # noqa
from app.modules.script.model import TVariableDataset  # noqa
from app.modules.usercenter.model import TPermission  # noqa
from app.modules.usercenter.model import TPermissionModule  # noqa
from app.modules.usercenter.model import TPermissionObject  # noqa
from app.modules.usercenter.model import TRole  # noqa
from app.modules.usercenter.model import TUser  # noqa
from app.modules.usercenter.model import TUserLoginInfo  # noqa
from app.modules.usercenter.model import TUserPassword  # noqa
from app.modules.usercenter.model import TUserRole  # noqa
from app.tools.identity import new_id
from app.tools.security import encrypt_password


from app.modules.opencenter.model import *  # noqa isort:skip
from app.modules.script.model import *      # noqa isort:skip
from app.modules.system.model import *      # noqa isort:skip
from app.modules.public.model import *      # noqa isort:skip
from app.modules.usercenter.model import *  # noqa isort:skip


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
@click.option('-m', '--confirm', help='删除库表前需要输入确认信息，注意：该命令仅用于开发环境！！！')
@with_appcontext
def dropdb(confirm):
    if not confirm:
        click.echo('请输入确认信息')
        return
    if confirm != 'confirmed':
        click.echo('确认信息不正确，请重试')
        return
    db.drop_all()
    click.echo('删除所有库表成功')


@click.command()
def initdata():
    """初始化数据"""
    init_user()
    init_role()
    init_permission()
    init_user_role()
    init_global_variable_dataset()
    db.session.commit()
    click.echo('初始化数据成功')


@with_appcontext
def init_user():
    """初始化用户"""
    # 创建系统用户
    TUser.norecord_insert(USER_NO='9999', USER_NAME='系统')
    # 创建管理员用户
    user_no = new_id()
    TUser.norecord_insert(USER_NO=user_no, USER_NAME='超级管理员')
    TUserLoginInfo.norecord_insert(USER_NO=user_no, LOGIN_NAME='admin', LOGIN_TYPE='ACCOUNT')
    TUserPassword.norecord_insert(
        USER_NO=user_no,
        PASSWORD=encrypt_password('admin', 'admin'),
        PASSWORD_TYPE='LOGIN',
        ERROR_TIMES=0,
        CREATE_TYPE='CUSTOMER'
    )
    # 创建管理员空间
    workspace_no = new_id()
    TWorkspace.norecord_insert(
        WORKSPACE_NO=workspace_no,
        WORKSPACE_NAME='个人空间',
        WORKSPACE_SCOPE='PRIVATE'
    )
    TWorkspaceUser.norecord_insert(WORKSPACE_NO=workspace_no, USER_NO=user_no)
    # 创建空间变量
    TVariableDataset.insert(
        WORKSPACE_NO=workspace_no,
        DATASET_NO=new_id(),
        DATASET_NAME='空间变量',
        DATASET_TYPE='WORKSPACE',
        DATASET_WEIGHT=2
    )
    # 创建空间元素
    TTestElement.insert(
        ELEMENT_NO=workspace_no,
        ELEMENT_NAME='空间元素',
        ELEMENT_TYPE='WORKSPACE',
        ELEMENT_CLASS='TestWorkspace'
    )
    click.echo('创建初始用户成功')


@with_appcontext
def init_role():
    """初始化角色"""
    create_role(name='超级管理员', code='ADMIN', rank='9999')
    create_role(name='系统管理员', code='SYSTEM', rank='9000')
    create_role(name='空间管理员', code='WORKSPACE', rank='8000')
    create_role(name='领导', code='LEADER', rank='4000')
    create_role(name='部门主管', code='DEPARTMENT', rank='3000')
    create_role(name='团队主管', code='TEAM', rank='2000')
    create_role(name='组长', code='GROUP', rank='1000')
    create_role(name='默认', code='DEFAULT', rank='1')

    click.echo('创建角色成功')


@with_appcontext
def init_permission():
    init_permission_module()
    init_permission_object()
    init_permission_item()
    click.echo('创建权限成功')


@with_appcontext
def init_permission_module():
    TPermissionModule.norecord_insert(MODULE_NO=new_id(), MODULE_NAME='用户中心', MODULE_CODE='USERCENTER')
    TPermissionModule.norecord_insert(MODULE_NO=new_id(), MODULE_NAME='系统', MODULE_CODE='SYSTEM')
    TPermissionModule.norecord_insert(MODULE_NO=new_id(), MODULE_NAME='公共', MODULE_CODE='PUBLIC')
    TPermissionModule.norecord_insert(MODULE_NO=new_id(), MODULE_NAME='脚本', MODULE_CODE='SCRIPT')
    TPermissionModule.norecord_insert(MODULE_NO=new_id(), MODULE_NAME='调度', MODULE_CODE='SCHEDULER')
    TPermissionModule.norecord_insert(MODULE_NO=new_id(), MODULE_NAME='开放中心', MODULE_CODE='OPENCENTER')


@with_appcontext
def init_permission_object():
    # USERCENTER
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='用户', OBJECT_CODE='USER')
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='分组', OBJECT_CODE='GROUP')
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='角色', OBJECT_CODE='ROLE')
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='权限', OBJECT_CODE='PERMISSION')
    # SYSTEM
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='日志', OBJECT_CODE='LOG')
    # PUBLIC
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='空间', OBJECT_CODE='WORKSPACE')
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='标签', OBJECT_CODE='TAG')
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='消息', OBJECT_CODE='MESSAGE')
    # SCRIPT
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='元素', OBJECT_CODE='ELEMENT')
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='变量', OBJECT_CODE='VARIABLE')
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='HTTP请求头', OBJECT_CODE='HTTP_HEADER')
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='数据库', OBJECT_CODE='DATABASE')
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='测试计划', OBJECT_CODE='TESTPLAN')
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='测试报告', OBJECT_CODE='TESTREPORT')
    # SCHEDULE
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='定时任务', OBJECT_CODE='JOB')
    # OPENCENTER
    TPermissionObject.norecord_insert(OBJECT_NO=new_id(), OBJECT_NAME='第三方应用', OBJECT_CODE='THIRD_PARTY_APP')


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
    create_permission('USERCENTER', 'USER', '查询用户', 'QUERY_USER', 'QUERY')
    create_permission('USERCENTER', 'USER', '新增用户', 'CREATE_USER', 'CREATE')
    create_permission('USERCENTER', 'USER', '修改用户', 'MODIFY_USER', 'MODIFY')
    create_permission('USERCENTER', 'USER', '重置密码', 'RESET_PASSWORD', 'MODIFY')
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
    # job
    create_permission('SCHEDULER', 'JOB', '查询定时任务', 'QUERY_JOB', 'QUERY')
    create_permission('SCHEDULER', 'JOB', '新增定时任务', 'CREATE_JOB', 'CREATE')
    create_permission('SCHEDULER', 'JOB', '修改定时任务', 'MODIFY_JOB', 'MODIFY')
    create_permission('SCHEDULER', 'JOB', '暂停定时任务', 'PAUSE_JOB', 'PAUSE')
    create_permission('SCHEDULER', 'JOB', '恢复定时任务', 'RESUME_JOB', 'RESUME')
    create_permission('SCHEDULER', 'JOB', '关闭定时任务', 'REMOVE_JOB', 'REMOVE')
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
    create_permission('SCRIPT', 'ELEMENT', '查询脚本(JSON)', 'QUERY_SCRIPT_AS_JSON', 'QUERY')
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
    role = TRole.filter_by(ROLE_CODE='ADMIN').first()
    TUserRole.norecord_insert(USER_NO=user.USER_NO, ROLE_NO=role.ROLE_NO)
    click.echo('创建用户角色关联成功')


@with_appcontext
def init_global_variable_dataset():
    TVariableDataset.norecord_insert(
        DATASET_NO=new_id(),
        DATASET_NAME='全局变量',
        DATASET_TYPE='GLOBAL',
        DATASET_WEIGHT=1
    )
    click.echo('初始化PyMeter全局变量成功')


def create_role(name, code, rank):
    TRole.norecord_insert(ROLE_NO=new_id(), ROLE_NAME=name, ROLE_CODE=code, ROLE_RANK=rank, ROLE_TYPE='SYSTEM')


def create_permission(module_code, object_code, name, code, act):
    permission_no = new_id()
    TPermission.norecord_insert(
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
    from app.modules.opencenter import model as opencenter_model
    from app.modules.public import model as public_model
    from app.modules.schedule import model as schedule_model
    from app.modules.script import model as script_model
    from app.modules.system import model as system_model
    from app.modules.usercenter import model as usercenter_model

    engine = create_engine(CONFIG.DB_URL)

    if hasattr(opencenter_model, name):
        table = getattr(opencenter_model, name)
    elif hasattr(public_model, name):
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
