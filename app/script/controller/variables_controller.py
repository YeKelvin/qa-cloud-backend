#!/usr/bin/ python3
# @File    : variables_controller.py
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from app.script.controller import blueprint
from app.script.enum import VariableDatasetType
from app.script.service import variables_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.parser import ListParser


@blueprint.get('/variable/dataset/list')
@require_login
@require_permission('QUERY_DATASET')
def query_variable_dataset_list():
    """分页查询变量集列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('datasetNo'),
        Argument('datasetName'),
        Argument('datasetType'),
        Argument('datasetDesc'),
        Argument('page', required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_variables_dataset_list(req)


@blueprint.get('/variable/dataset/all')
@require_login
@require_permission('QUERY_DATASET')
def query_variable_dataset_all():
    """查询所有变量集"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('datasetType')
    ).parse()
    return service.query_variable_dataset_all(req)


@blueprint.get('/variable/dataset/all/in/private')
@require_login
@require_permission('QUERY_DATASET')
def query_variable_dataset_all_in_private():
    """根据用户空间查询全部变量集"""
    req = JsonParser(
        Argument('datasetType')
    ).parse()
    return service.query_variable_dataset_all_in_private(req)


@blueprint.post('/variable/dataset')
@require_login
@require_permission('CREATE_DATASET')
def create_variable_dataset():
    """新增变量集"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('datasetName', required=True, nullable=False, help='变量集名称不能为空'),
        Argument('datasetType', required=True, nullable=False, enum=VariableDatasetType, help='变量集类型不能为空'),
        Argument('datasetDesc')
    ).parse()
    return service.create_variable_dataset(req)


@blueprint.put('/variable/dataset')
@require_login
@require_permission('MODIFY_DATASET')
def modify_variable_dataset():
    """修改变量集"""
    req = JsonParser(
        Argument('datasetNo', required=True, nullable=False, help='变量集编号不能为空'),
        Argument('datasetName', required=True, nullable=False, help='变量集名称不能为空'),
        Argument('datasetDesc')
    ).parse()
    return service.modify_variable_dataset(req)


@blueprint.delete('/variable/dataset')
@require_login
@require_permission('REMOVE_DATASET')
def remove_variable_dataset():
    """删除变量集"""
    req = JsonParser(
        Argument('datasetNo', required=True, nullable=False, help='变量集编号不能为空')
    ).parse()
    return service.remove_variable_dataset(req)


@blueprint.post('/variable')
@require_login
@require_permission('CREATE_VARIABLE')
def create_variable():
    """新增变量"""
    req = JsonParser(
        Argument('datasetNo', required=True, nullable=False, help='变量集编号不能为空'),
        Argument('varName', required=True, nullable=False, help='变量名称不能为空'),
        Argument('varDesc'),
        Argument('initialValue'),
        Argument('currentValue')
    ).parse()
    return service.create_variable(req)


@blueprint.put('/variable')
@require_login
@require_permission('MODIFY_VARIABLE')
def modify_variable():
    """修改变量"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空'),
        Argument('varName', required=True, nullable=False, help='变量名称不能为空'),
        Argument('varDesc'),
        Argument('initialValue'),
        Argument('currentValue')
    ).parse()
    return service.modify_variable(req)


@blueprint.delete('/variable')
@require_login
@require_permission('REMOVE_VARIABLE')
def remove_variable():
    """删除变量"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空')
    ).parse()
    return service.remove_variable(req)


@blueprint.patch('/variable/enable')
@require_login
@require_permission('MODIFY_VARIABLE')
def enable_variable():
    """启用变量"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空')
    ).parse()
    return service.enable_variable(req)


@blueprint.patch('/variable/disable')
@require_login
@require_permission('MODIFY_VARIABLE')
def disable_variable():
    """禁用变量"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空')
    ).parse()
    return service.disable_variable(req)


@blueprint.patch('/variable/current/value')
@require_login
@require_permission('MODIFY_VARIABLE')
def update_current_value():
    """更新变量当前值"""
    req = JsonParser(
        Argument('varNo', required=True, nullable=False, help='变量编号不能为空'),
        Argument('value')
    ).parse()
    return service.update_current_value(req)


@blueprint.get('/variables/by/dataset')
@require_login
@require_permission('QUERY_VARIABLE')
def query_variables_by_dataset():
    """根据集合查询全部变量"""
    req = JsonParser(
        Argument('datasetNo', required=True, nullable=False, help='变量集编号不能为空')
    ).parse()
    return service.query_variable_by_dataset(req)


@blueprint.get('/variables')
@require_login
@require_permission('QUERY_VARIABLE')
def query_variables():
    """
    根据列表批量查询变量
    example: ['dataset_no', 'dataset_no']
    """
    req = ListParser().parse()
    return service.query_variables(req)


@blueprint.post('/variables')
@require_login
@require_permission('CREATE_VARIABLE')
def create_variables():
    """
    根据列表批量新增变量

    example:
    {
        "datasetNo": "",
        "variableList": [
            {
                "varName": "",
                "varDesc": "",
                "initialValue": "",
                "currentValue": ""
            }
            ...
        ]
    }
    """
    req = JsonParser(
        Argument('datasetNo', required=True, nullable=False, help='变量集编号不能为空'),
        Argument('variableList', type=list, required=True, nullable=False, help='变量列表不能为空')
    ).parse()
    return service.create_variables(req)


@blueprint.put('/variables')
@require_login
@require_permission('MODIFY_VARIABLE')
def modify_variables():
    """
    根据列表批量修改变量

    example:
    {
        "datasetNo": "",
        "variableList": [
            {
                "varNo": "",
                "varName": "",
                "varDesc": "",
                "initialValue": "",
                "currentValue": ""
            }
            ...
        ]
    }
    """
    req = JsonParser(
        Argument('datasetNo', required=True, nullable=False, help='变量集编号不能为空'),
        Argument('variableList', type=list, required=True, nullable=False, help='变量列表不能为空')
    ).parse()
    return service.modify_variables(req)


@blueprint.delete('/variables')
@require_login
@require_permission('REMOVE_VARIABLE')
def remove_variables():
    """批量删除变量"""
    req = JsonParser(
        Argument('datasetNo', required=True, nullable=False, help='变量集编号不能为空'),
        Argument('variableNos', type=list, required=True, nullable=False, help='变量列表不能为空')
    ).parse()
    return service.remove_variables(req)


@blueprint.post('/variable/dataset/duplicate')
@require_login
@require_permission('COPY_DATASET')
def duplicate_variable_dataset():
    """复制变量集"""
    req = JsonParser(
        Argument('datasetNo', required=True, nullable=False, help='变量集编号不能为空')
    ).parse()
    return service.duplicate_variable_dataset(req)


@blueprint.post('/variable/dataset/copy/to/workspace')
@require_login
@require_permission('COPY_DATASET')
def copy_variable_dataset_to_workspace():
    """复制变量集到指定工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('datasetNo', required=True, nullable=False, help='变量集编号不能为空')
    ).parse()
    return service.copy_variable_dataset_to_workspace(req)


@blueprint.post('/variable/dataset/move/to/workspace')
@require_login
@require_permission('MOVE_DATASET')
def move_variable_dataset_to_workspace():
    """移动变量集到指定工作空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('datasetNo', required=True, nullable=False, help='变量集编号不能为空')
    ).parse()
    return service.move_variable_dataset_to_workspace(req)
