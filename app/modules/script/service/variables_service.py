#!/usr/bin/ python3
# @File    : variables_service.py
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from sqlalchemy import and_

from app.modules.script.dao import variable_dao
from app.modules.script.dao import variable_dataset_dao
from app.modules.script.enum import VariableDatasetType
from app.modules.script.enum import VariableDatasetWeight
from app.modules.script.model import TVariable
from app.modules.script.model import TVariableDataset
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.tools.validator import check_workspace_permission
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_dataset_list(req):
    # 条件查询
    conds = QueryCondition()
    conds.like(TVariableDataset.WORKSPACE_NO, req.workspaceNo)
    conds.like(TVariableDataset.DATASET_NO, req.datasetNo)
    conds.like(TVariableDataset.DATASET_NAME, req.datasetName)
    conds.like(TVariableDataset.DATASET_TYPE, req.datasetType)
    conds.like(TVariableDataset.DATASET_DESC, req.datasetDesc)

    # 条件分页查询
    pagination = (
        TVariableDataset
        .filter(*conds)
        .order_by(TVariableDataset.DATASET_WEIGHT.desc(), TVariableDataset.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'datasetNo': item.DATASET_NO,
            'datasetName': item.DATASET_NAME,
            'datasetType': item.DATASET_TYPE,
            'datasetDesc': item.DATASET_DESC,
            'datasetBinding': item.DATASET_BINDING
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


@http_service
def query_dataset_all(req):
    # 条件查询
    conds = QueryCondition()
    conds.equal(TVariableDataset.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TVariableDataset.DATASET_TYPE, req.datasetType)

    results = (
        TVariableDataset
        .filter(and_(*conds) | (TVariableDataset.DATASET_TYPE == VariableDatasetType.GLOBAL.value))
        .order_by(TVariableDataset.DATASET_WEIGHT.desc(), TVariableDataset.CREATED_TIME.desc())
        .all()
    )

    return [
        {
            'datasetNo': item.DATASET_NO,
            'datasetName': item.DATASET_NAME,
            'datasetType': item.DATASET_TYPE,
            'datasetDesc': item.DATASET_DESC,
            'datasetBinding': item.DATASET_BINDING
        }
        for item in results
    ]


@http_service
def create_dataset(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 查询变量集信息
    dataset = variable_dataset_dao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NAME=req.datasetName,
        DATASET_TYPE=req.datasetType
    )
    check_not_exists(dataset, error_msg='变量集已存在')

    # 变量集为ENVIRONMENT或CUSTOM时，工作空间编号不能为空
    if req.datasetType != VariableDatasetType.GLOBAL.value and not req.workspaceNo:
        raise ServiceError('工作空间编号不能为空')

    # 新增变量集
    dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NO=dataset_no,
        DATASET_NAME=req.datasetName,
        DATASET_TYPE=req.datasetType,
        DATASET_DESC=req.datasetDesc,
        DATASET_WEIGHT=VariableDatasetWeight[req.datasetType].value,
        DATASET_BINDING=req.datasetBinding
    )

    return {'datasetNo': dataset_no}


@http_service
def modify_dataset(req):
    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error_msg='变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 更新变量集信息
    dataset.update(
        DATASET_NAME=req.datasetName,
        DATASET_DESC=req.datasetDesc,
        DATASET_BINDING=req.datasetBinding
    )


@http_service
def remove_dataset(req):
    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error_msg='变量集不存在')
    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)
    # 删除变量集下的所有变量
    variable_dao.delete_all_by_dataset(req.datasetNo)
    # 删除变量集
    dataset.delete()


@http_service
def create_variable(req):
    # 查询变量信息
    variable = variable_dao.select_by_dataset_and_name(req.datasetNo, req.varName)
    check_not_exists(variable, error_msg='变量集已存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error_msg='变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 新增变量
    var_no = new_id()
    TVariable.insert(
        DATASET_NO=req.datasetNo,
        VAR_NO=var_no,
        VAR_NAME=req.varName.strip() if req.varName else req.varName,
        VAR_DESC=req.varDesc.strip() if req.varDesc else req.varDesc,
        INITIAL_VALUE=req.initialValue.strip() if req.initialValue else req.initialValue,
        CURRENT_VALUE=req.currentValue.strip() if req.currentValue else req.currentValue,
        ENABLED=True
    )

    return var_no


@http_service
def modify_variable(req):
    # 查询变量信息
    variable = variable_dao.select_by_no(req.varNo)
    check_exists(variable, error_msg='变量不存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, error_msg='变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 更新变量信息
    variable.update(
        VAR_NAME=req.varName.strip() if req.varName else req.varName,
        VAR_DESC=req.varDesc.strip() if req.varDesc else req.varDesc,
        INITIAL_VALUE=req.initialValue.strip() if req.initialValue else req.initialValue,
        CURRENT_VALUE=req.currentValue.strip() if req.currentValue else req.currentValue
    )


@http_service
def remove_variable(req):
    # 查询变量信息
    variable = variable_dao.select_by_no(req.varNo)
    check_exists(variable, error_msg='变量不存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, error_msg='变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 删除变量
    variable.delete()


@http_service
def enable_variable(req):
    # 查询变量信息
    variable = variable_dao.select_by_no(req.varNo)
    check_exists(variable, error_msg='变量不存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, error_msg='变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 启用变量
    variable.update(
        ENABLED=True
    )


@http_service
def disable_variable(req):
    # 查询变量信息
    variable = variable_dao.select_by_no(req.varNo)
    check_exists(variable, error_msg='变量不存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, error_msg='变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 禁用变量
    variable.update(
        ENABLED=False
    )


@http_service
def update_current_value(req):
    # 查询变量信息
    variable = variable_dao.select_by_no(req.varNo)
    check_exists(variable, error_msg='变量不存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, error_msg='变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 更新当前值
    variable.update(
        CURRENT_VALUE=req.value.strip() if req.value else req.value
    )


@http_service
def query_variable_by_dataset(req):
    variables = variable_dao.select_all_by_dataset(req.datasetNo)

    return [
        {
            'varNo': variable.VAR_NO,
            'varName': variable.VAR_NAME,
            'varDesc': variable.VAR_DESC,
            'initialValue': variable.INITIAL_VALUE,
            'currentValue': variable.CURRENT_VALUE,
            'enabled': variable.ENABLED
        }
        for variable in variables
    ]


@http_service
def query_variables(req):
    result = []
    for dataset_no in req.datasets:
        # 查询变量集信息
        dataset = variable_dataset_dao.select_by_no(dataset_no)
        if not dataset:
            continue

        # 查询变量列表
        variables = variable_dao.select_all_by_dataset(dataset_no)

        result.extend(
            {
                'datasetNo': dataset.DATASET_NO,
                'datasetName': dataset.DATASET_NAME,
                'varNo': variable.VAR_NO,
                'varName': variable.VAR_NAME,
                'varDesc': variable.VAR_DESC,
                'initialValue': variable.INITIAL_VALUE,
                'currentValue': variable.CURRENT_VALUE,
                'enabled': variable.ENABLED
            }
            for variable in variables
        )

    return result


@http_service
def create_variables(req):
    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error_msg='变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    for vari in req.variableList:
        # 跳过变量名为空的数据
        if not vari.varName:
            continue

        # 查询变量信息
        variable = variable_dao.select_by_dataset_and_name(req.datasetNo, vari.varName)
        check_not_exists(variable, error_msg='变量已存在')

        # 新增变量
        TVariable.insert(
            DATASET_NO=req.datasetNo,
            VAR_NO=new_id(),
            VAR_NAME=vari.varName.strip() if vari.varName else vari.varName,
            VAR_DESC=vari.varDesc.strip() if vari.varDesc else vari.varDesc,
            INITIAL_VALUE=vari.initialValue.strip() if vari.initialValue else vari.initialValue,
            CURRENT_VALUE=vari.currentValue.strip() if vari.currentValue else vari.currentValue,
            ENABLED=True
        )


@http_service
def modify_variables(req):
    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error_msg='变量集不存在')
    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)
    # 遍历更新变量
    for vari in req.variableList:
        # 跳过变量名为空的数据
        if not vari.varName:
            continue

        if 'varNo' in vari:
            # 查询变量信息
            variable = variable_dao.select_by_no(vari.varNo)
            check_exists(variable, error_msg='变量不存在')
            # 更新变量信息
            variable.update(
                VAR_NAME=vari.varName.strip() if vari.varName else vari.varName,
                VAR_DESC=vari.varDesc.strip() if vari.varDesc else vari.varDesc,
                INITIAL_VALUE=vari.initialValue.strip() if vari.initialValue else vari.initialValue,
                CURRENT_VALUE=vari.currentValue.strip() if vari.currentValue else vari.currentValue,
            )
        else:
            # 查询变量信息
            variable = variable_dao.select_by_dataset_and_name(req.datasetNo, vari.varName)
            check_not_exists(variable, error_msg='变量已存在')
            # 新增变量
            TVariable.insert(
                DATASET_NO=req.datasetNo,
                VAR_NO=new_id(),
                VAR_NAME=vari.varName.strip() if vari.varName else vari.varName,
                VAR_DESC=vari.varDesc.strip() if vari.varDesc else vari.varDesc,
                INITIAL_VALUE=vari.initialValue.strip() if vari.initialValue else vari.initialValue,
                CURRENT_VALUE=vari.currentValue.strip() if vari.currentValue else vari.currentValue,
                ENABLED=True
            )


@http_service
def remove_variables(req):
    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error_msg='变量集不存在')
    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)
    # 批量删除变量
    variable_dao.delete_in_no(req.variables)


@http_service
def duplicate_dataset(req):
    # 查询变量集
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error_msg='变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 复制变量集
    new_dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=dataset.WORKSPACE_NO,
        DATASET_NO=new_dataset_no,
        DATASET_NAME=f'{dataset.DATASET_NAME} copy',
        DATASET_TYPE=dataset.DATASET_TYPE,
        DATASET_DESC=dataset.DATASET_DESC,
        DATASET_WEIGHT=dataset.DATASET_WEIGHT
    )

    # 复制变量
    variables = variable_dao.select_all_by_dataset(req.datasetNo)
    for variable in variables:
        TVariable.insert(
            DATASET_NO=new_dataset_no,
            VAR_NO=new_id(),
            VAR_NAME=variable.VAR_NAME,
            VAR_DESC=variable.VAR_DESC,
            INITIAL_VALUE=variable.INITIAL_VALUE,
            CURRENT_VALUE=variable.CURRENT_VALUE,
            ENABLED=True
        )

    return {'datasetNo': new_dataset_no}


@http_service
def copy_dataset_to_workspace(req):
    # 查询变量集
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error_msg='变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 复制变量集
    new_dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NO=new_dataset_no,
        DATASET_NAME=f'{dataset.DATASET_NAME} copy',
        DATASET_TYPE=dataset.DATASET_TYPE,
        DATASET_DESC=dataset.DATASET_DESC,
        DATASET_WEIGHT=dataset.DATASET_WEIGHT
    )

    # 复制变量
    variables = variable_dao.select_all_by_dataset(req.datasetNo)
    for variable in variables:
        TVariable.insert(
            DATASET_NO=new_dataset_no,
            VAR_NO=new_id(),
            VAR_NAME=variable.VAR_NAME,
            VAR_DESC=variable.VAR_DESC,
            INITIAL_VALUE=variable.INITIAL_VALUE,
            CURRENT_VALUE=variable.CURRENT_VALUE,
            ENABLED=True
        )

    return {'datasetNo': new_dataset_no}


@http_service
def move_dataset_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)
    # 查询变量集
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error_msg='变量集不存在')
    # 移动变量集
    dataset.update(WORKSPACE_NO=req.workspaceNo)
