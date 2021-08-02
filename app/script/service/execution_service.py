#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_service.py
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
import traceback

from pymeter.runner import Runner

from app.common.decorators.service import http_service
from app.common.validator import check_is_not_blank
from app.extension import executor
from app.extension import socketio
from app.script.dao import element_child_rel_dao as ElementChildRelDao, variable_dao, variable_set_dao
from app.script.dao import element_property_dao as ElementPropertyDao
from app.script.model import TTestElement
from app.utils.json_util import from_json
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def execute_script(req):
    # 根据collectionNo递归查询脚本数据并转换成dict
    collection = load_element(req.collectionNo)

    # TODO: 增加脚本完整性校验，例如脚本下是否有内容

    if req.sid:
        add_flask_socketio_result_collector(collection, req.sid)

    if req.variableSet:
        add_variable_data_set(collection, req.variableSet)

    script = [collection]

    # 新增线程执行脚本
    def start():
        sid = req.sid
        try:
            Runner.start(script, throw_ex=True)
        except Exception:
            log.error(traceback.format_exc())
            socketio.emit('pymeter_error', '脚本执行异常，请联系管理员', namespace='/', to=sid)

    # TODO: 暂时用ThreadPoolExecutor，后面改用Celery，https://www.celerycn.io/
    executor.submit(start)
    return None


def add_flask_socketio_result_collector(script: dict, sid: str):
    script['children'].insert(
        0, {
            'name': 'FlaskSocketIOResultCollector',
            'remark': None,
            'class': 'FlaskSocketIOResultCollector',
            'enabled': True,
            'property': {
                'FlaskSocketIOResultCollector__namespace': '/',
                'FlaskSocketIOResultCollector__event_name': 'pymeter_result',
                'FlaskSocketIOResultCollector__target_sid': sid,
                'FlaskSocketIOResultCollector__flask_sio_instance_module': 'app.extension',
                'FlaskSocketIOResultCollector__flask_sio_instance_name': 'socketio',
            },
            'children': None
        }
    )


def load_element(element_no):
    # 查询元素
    element = TTestElement.query_by(ELEMENT_NO=element_no).first()
    check_is_not_blank(element, '测试元素不存在')

    # 递归查询元素子代
    # 查询时根据 order asc 排序
    element_child_rel_list = ElementChildRelDao.select_all_by_parentno(element_no)

    children = []
    if element_child_rel_list:
        for element_child_rel in element_child_rel_list:
            children.append(load_element(element_child_rel.CHILD_NO))

    info = {
        'name': element.ELEMENT_NAME,
        'remark': element.ELEMENT_REMARK,
        'class': element.ELEMENT_CLASS,
        'enabled': element.ENABLED,
        'property': load_element_property(element_no),
        'children': children
    }
    return info


def load_element_property(element_no):
    # 查询元素属性，只查询enabled的属性
    props = ElementPropertyDao.select_all_by_elementno_with_enable(element_no)

    property = {}
    for prop in props:
        if prop.PROPERTY_TYPE == 'STR':
            property[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE
            continue
        if prop.PROPERTY_TYPE == 'DICT':
            property[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
            continue
        if prop.PROPERTY_TYPE == 'LIST':
            property[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
            continue

    return property


def get_variables_by_setlist(set_list, use_current_value):
    result = {}
    for set_no in set_list:
        # 查询变量列表
        variables = variable_dao.select_list_by_setno(set_no)

        for variable in variables:
            if not variable.ENABLED:
                continue
            if use_current_value and variable.CURRENT_VALUE:
                result[variable.VAR_NAME] = variable.CURRENT_VALUE
            else:
                result[variable.VAR_NAME] = variable.INITIAL_VALUE

    return result


def add_variable_data_set(script: dict, variable_set):
    variables = get_variables_by_setlist(variable_set.list, variable_set.use_current_value)
    arguments = []
    for name, value in variables.items():
        arguments.append({'class': 'Argument', 'property': {'Argument__name': name, 'Argument__value': value}})

    script['children'].insert(
        0, {
            'name': '变量配置器',
            'remark': '',
            'class': 'VariableDataSet',
            'enabled': True,
            'property': {
                'Arguments__arguments': arguments
            }
        }
    )
