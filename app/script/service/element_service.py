#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_service.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from typing import Iterable
from typing import List

from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.exceptions import ServiceError
from app.common.id_generator import new_id
from app.common.validator import check_is_not_blank
from app.extension import db
from app.public.dao import workspace_dao as WorkspaceDao
from app.public.model import TWorkspace
from app.script.dao import element_builtin_child_rel_dao as ElementBuiltinChildRelDao
from app.script.dao import element_child_rel_dao as ElementChildRelDao
from app.script.dao import element_property_dao as ElementPropertyDao
from app.script.dao import http_headers_template_dao as HttpHeadersTemplateDao
from app.script.dao import http_sampler_headers_rel_dao as HttpSamplerHeadersRelDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.enum import ElementClass
from app.script.enum import ElementStatus
from app.script.enum import ElementType
from app.script.enum import PasteType
from app.script.enum import is_collection
from app.script.enum import is_config
from app.script.enum import is_controller
from app.script.enum import is_group
from app.script.enum import is_listener
from app.script.enum import is_sampler
from app.script.enum import is_test_collection
from app.script.enum import is_timer
from app.script.model import TElementBuiltinChildRel
from app.script.model import TElementChildRel
from app.script.model import TElementProperty
from app.script.model import THttpSamplerHeadersRel
from app.script.model import TTestElement
from app.script.model import TWorkspaceCollectionRel
from app.utils.json_util import from_json
from app.utils.json_util import to_json
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_element_list(req):
    # 查询条件
    conds = QueryCondition(TTestElement)
    conds.like(TTestElement.ELEMENT_NO, req.elementNo)
    conds.like(TTestElement.ELEMENT_NAME, req.elementName)
    conds.like(TTestElement.ELEMENT_REMARK, req.elementRemark)
    conds.like(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.like(TTestElement.ELEMENT_CLASS, req.elementClass)
    conds.like(TTestElement.ENABLED, req.enabled)

    if req.workspaceNo:
        conds.add_table(TWorkspaceCollectionRel)
        conds.equal(TWorkspaceCollectionRel.DECOLLECTION_NOL_STATE, TTestElement.ELEMENT_NO)
        conds.like(TWorkspaceCollectionRel.WORKSPACE_NO, req.workspaceNo)

    if req.workspaceName:
        conds.add_table(TWorkspace)
        conds.equal(TWorkspaceCollectionRel.DEL_STATE, 0)
        conds.equal(TWorkspaceCollectionRel.COLLECTION_NO, TTestElement.ELEMENT_NO)
        conds.equal(TWorkspaceCollectionRel.WORKSPACE_NO, TWorkspace.WORKSPACE_NO)
        conds.like(TWorkspace.WORKSPACE_NAME, req.workspaceName)

    # TTestElement，TWorkspace，TWorkspaceCollectionRel连表查询
    pagination = db.session.query(
        TTestElement.ELEMENT_NO, TTestElement.ELEMENT_NAME, TTestElement.ELEMENT_REMARK, TTestElement.ELEMENT_TYPE,
        TTestElement.ENABLED
    ).filter(*conds).order_by(TTestElement.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'enabled': item.ENABLED
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_element_all(req):
    # 查询条件
    conds = QueryCondition(TTestElement, TWorkspaceCollectionRel)
    conds.equal(TWorkspaceCollectionRel.COLLECTION_NO, TTestElement.ELEMENT_NO)
    conds.like(TWorkspaceCollectionRel.WORKSPACE_NO, req.workspaceNo)
    conds.like(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.like(TTestElement.ELEMENT_CLASS, req.elementClass)
    conds.like(TTestElement.ENABLED, req.enabled)

    # TTestElement，TWorkspaceCollectionRel连表查询
    items = db.session.query(
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_REMARK,
        TTestElement.ELEMENT_TYPE,
        TTestElement.ELEMENT_CLASS,
        TTestElement.ENABLED
    ).filter(*conds).order_by(TTestElement.CREATED_TIME.desc()).all()

    result = []
    for item in items:
        result.append({
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'elementClass': item.ELEMENT_CLASS,
            'enabled': item.ENABLED
        })
    return result


@http_service
def query_element_info(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    # 查询元素属性
    properties = query_element_property(req.elementNo)

    return {
        'elementNo': element.ELEMENT_NO,
        'elementName': element.ELEMENT_NAME,
        'elementRemark': element.ELEMENT_REMARK,
        'elementType': element.ELEMENT_TYPE,
        'elementClass': element.ELEMENT_CLASS,
        'enabled': element.ENABLED,
        'property': properties
    }


def query_element_property(element_no):
    """查询元素属性"""
    properties = {}
    props = ElementPropertyDao.select_all_by_element(element_no)
    for prop in props:
        if prop.PROPERTY_TYPE == 'DICT':
            properties[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
        elif prop.PROPERTY_TYPE == 'LIST':
            properties[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
        else:
            properties[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE
    return properties


@http_service
def query_element_children(req):
    return get_element_children(req.elementNo, req.depth)


@http_service
def query_elements_children(req):
    result = []
    for element_no in req.elementNumberList:
        element = TestElementDao.select_by_no(element_no)
        if not element:
            log.warning(f'elementNo:[ {element_no} ] 元素不存在')
            continue
        children = get_element_children(element_no, req.depth)
        result.append({
            'rootNo': get_root_no(element_no),
            'elementNo': element.ELEMENT_NO,
            'elementName': element.ELEMENT_NAME,
            'elementType': element.ELEMENT_TYPE,
            'elementClass': element.ELEMENT_CLASS,
            'enabled': element.ENABLED,
            'children': children
        })

    return result


def get_element_children(parent_no, depth):
    """递归查询元素子代"""
    result = []
    # 查询元素所有子代关系
    child_rel_list = ElementChildRelDao.select_all_by_parent(parent_no)
    if not child_rel_list:
        return result

    # 根据序号排序
    child_rel_list.sort(key=lambda k: k.SERIAL_NO)
    for child_rel in child_rel_list:
        # 查询子代元素
        element = TestElementDao.select_by_no(child_rel.CHILD_NO)
        if element:
            # 递归查询子代
            children = depth and get_element_children(child_rel.CHILD_NO, depth) or []
            result.append({
                'rootNo': child_rel.ROOT_NO,
                'elementNo': element.ELEMENT_NO,
                'elementName': element.ELEMENT_NAME,
                'elementType': element.ELEMENT_TYPE,
                'elementClass': element.ELEMENT_CLASS,
                'enabled': element.ENABLED,
                'serialNo': child_rel.SERIAL_NO,
                'children': children
            })

    return result


def get_root_no(element_no):
    """根据元素编号获取根元素编号（集合编号）"""
    rel = ElementChildRelDao.select_by_child(element_no)
    if rel:
        return rel.ROOT_NO
    else:
        return element_no


@http_service
@transactional
def create_element(req):
    if req.elementType == ElementType.COLLECTION.value and not req.workspaceNo:
        raise ServiceError('工作空间编号不能为空')

    # 创建元素
    element_no = add_element(
        element_name=req.elementName,
        element_remark=req.elementRemark,
        element_type=req.elementType,
        element_class=req.elementClass,
        properties=req.property
    )

    # 如果元素类型为 TestCollection 时，需要绑定 WorkspaceNo
    if req.workspaceNo:
        # 查询工作空间
        workspace = WorkspaceDao.select_by_no(req.workspaceNo)
        check_is_not_blank(workspace, '工作空间不存在')
        # 关联工作空间和测试集合
        TWorkspaceCollectionRel.insert(WORKSPACE_NO=req.workspaceNo, COLLECTION_NO=element_no)

    return {'elementNo': element_no}


def add_element(element_name, element_remark, element_type, element_class, properties: dict = None):
    """创建元素并递归创建元素属性和元素子代"""
    # 创建元素
    element_no = new_id()
    TTestElement.insert(
        ELEMENT_NO=element_no,
        ELEMENT_NAME=element_name,
        ELEMENT_REMARK=element_remark,
        ELEMENT_TYPE=element_type,
        ELEMENT_CLASS=element_class,
        ENABLED=ElementStatus.ENABLE.value
    )

    # 创建元素属性
    if properties:
        add_element_property(element_no, properties)

    return element_no


@http_service
@transactional
def create_element_children(req):
    return add_element_children(root_no=req.rootNo, parent_no=req.parentNo, children=req.children)


def add_element_children(root_no, parent_no, children: Iterable[dict]) -> List:
    """添加元素子代"""
    result = []
    for child in children:
        # 新建子代元素
        child_no = add_element(
            element_name=child.get('elementName'),
            element_remark=child.get('elementRemark'),
            element_type=child.get('elementType'),
            element_class=child.get('elementClass'),
            properties=child.get('property', None)
        )
        # 新建子代与父级关联
        TElementChildRel.insert(
            ROOT_NO=root_no,
            PARENT_NO=parent_no,
            CHILD_NO=child_no,
            SERIAL_NO=ElementChildRelDao.next_serial_number_by_parent(parent_no)
        )
        # 新建子代内置元素
        builtin = child.get('builtIn', None)
        if builtin:
            add_element_builtins(parent_no=child_no, children=builtin, root_no=root_no)
        result.append(child_no)
    return result


@http_service
@transactional
def modify_element(req):
    update_element(
        element_no=req.elementNo,
        element_name=req.elementName,
        element_remark=req.elementRemark,
        properties=req.property
    )


@http_service
@transactional
def modify_elements(req):
    for item in req.list:
        # 更新元素
        update_element(
            element_no=item.elementNo,
            element_name=item.elementName,
            element_remark=item.elementRemark,
            properties=item.property
        )
        # 更新内置元素
        if item.builtIn:
            update_element_builtins(item.builtIn)


def update_element(element_no, element_name, element_remark, properties: dict = None):
    # 查询元素
    element = TestElementDao.select_by_no(element_no)
    check_is_not_blank(element, '元素不存在')

    # 更新元素
    element.update(ELEMENT_NAME=element_name, ELEMENT_REMARK=element_remark)

    # 更新元素属性
    if properties:
        update_element_property(element_no, properties)


@http_service
@transactional
def remove_element(req):
    return delete_element(req.elementNo)


def delete_element(element_no):
    """递归删除元素"""
    # 查询元素
    element = TestElementDao.select_by_no(element_no)
    check_is_not_blank(element, '元素不存在')

    # 递归删除元素子代和子代关联
    delete_element_children(element_no)

    # 如果元素存在父级关联，则删除关联并重新排序子代元素
    delete_element_child_rel(element_no)

    # 如果存在内置元素，一并删除
    delete_element_builtins_by_parent(element_no)

    # 删除元素属性
    delete_element_property(element_no)

    # 删除元素
    element.delete()


def delete_element_children(parent_no):
    """递归删除子代元素（包含子代元素、子代属性、子代与父级关联、子代内置元素和子代内置元素属性）"""
    # 查询所有子代关联列表
    child_rel_list = ElementChildRelDao.select_all_by_parent(parent_no)
    for child_rel in child_rel_list:
        # 如果子代存在内置元素，一并删除
        delete_element_builtins_by_parent(child_rel.CHILD_NO)
        # 查询子代元素
        child = TestElementDao.select_by_no(child_rel.CHILD_NO)
        # 递归删除子代元素的子代和关联
        delete_element_children(child_rel.CHILD_NO)
        # 删除子代元素属性
        delete_element_property(child_rel.CHILD_NO)
        # 删除父子关联
        child_rel.delete()
        # 删除子代元素
        child.delete()


def delete_element_child_rel(child_no):
    # 如果子代存在父级关联，则删除关联并重新排序子代元素
    child_rel = ElementChildRelDao.select_by_child(child_no)
    if child_rel:
        # 重新排序父级子代
        TElementChildRel.filter(
            TElementChildRel.PARENT_NO == child_rel.PARENT_NO, TElementChildRel.SERIAL_NO > child_rel.SERIAL_NO
        ).update(
            {TElementChildRel.SERIAL_NO: TElementChildRel.SERIAL_NO - 1}
        )
        # 删除父级关联
        child_rel.delete()


def delete_element_property(element_no):
    # 查询所有元素属性
    props = ElementPropertyDao.select_all_by_element(element_no)
    for prop in props:
        prop.delete()


@http_service
def enable_element(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    # 更新元素状态为启用
    element.update(ENABLED=ElementStatus.ENABLE.value)


@http_service
def disable_element(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    # 更新元素状态为禁用
    element.update(ENABLED=ElementStatus.DISABLE.value)


def add_element_property(element_no, properties: dict):
    """遍历添加元素属性"""
    for name, value in properties.items():
        property_type = 'STR'
        if isinstance(value, dict):
            property_type = 'DICT'
            value = to_json(value)
        if isinstance(value, list):
            property_type = 'LIST'
            value = to_json(value)

        TElementProperty.insert(
            ELEMENT_NO=element_no, PROPERTY_NAME=name, PROPERTY_VALUE=value, PROPERTY_TYPE=property_type
        )


def update_element_property(element_no, properties: dict):
    """遍历修改元素属性"""
    for name, value in properties.items():
        # 查询元素属性
        prop = ElementPropertyDao.select_by_element_and_name(element_no, name)
        property_type = 'STR'
        if isinstance(value, dict):
            property_type = 'DICT'
            value = to_json(value)
        if isinstance(value, list):
            property_type = 'LIST'
            value = to_json(value)

        # 有属性就更新，没有就新增
        if prop:
            prop.update(PROPERTY_VALUE=value, PROPERTY_TYPE=property_type)
        else:
            TElementProperty.insert(
                ELEMENT_NO=element_no,
                PROPERTY_NAME=name,
                PROPERTY_VALUE=value,
                PROPERTY_TYPE=property_type
            )
    # 删除请求中没有的属性
    ElementPropertyDao.delete_all_by_element_and_notin_name(element_no, list(properties.keys()))


@http_service
@transactional
def move_element(req):
    # 查询 source 元素子代关联
    source_child_rel = ElementChildRelDao.select_by_child(req.sourceNo)
    check_is_not_blank(source_child_rel, 'source元素关联不存在')

    # 校验
    if req.targetSerialNo < 0:
        raise ServiceError('target元素序号不能小于0')

    # source 父元素编号
    source_parent_no = source_child_rel.PARENT_NO
    # source 元素序号
    source_serial_no = source_child_rel.SERIAL_NO

    # 父元素不变时，仅重新排序 source 同级元素
    if source_parent_no == req.targetParentNo:
        # 序号相等时直接跳过
        if req.targetSerialNo == source_child_rel.SERIAL_NO:
            return

        # 元素移动类型，上移或下移
        move_type = 'UP' if source_serial_no > req.targetSerialNo else 'DOWN'
        if move_type == 'UP':
            # 下移  [target, source) 区间元素
            TElementChildRel.filter(
                TElementChildRel.PARENT_NO == source_parent_no,
                TElementChildRel.SERIAL_NO < source_serial_no,
                TElementChildRel.SERIAL_NO >= req.targetSerialNo
            ).update({TElementChildRel.SERIAL_NO: TElementChildRel.SERIAL_NO + 1})
        else:
            # 上移  (source, target] 区间元素
            TElementChildRel.filter(
                TElementChildRel.PARENT_NO == source_parent_no,
                TElementChildRel.SERIAL_NO > source_serial_no,
                TElementChildRel.SERIAL_NO <= req.targetSerialNo,
            ).update({TElementChildRel.SERIAL_NO: TElementChildRel.SERIAL_NO - 1})
        # 更新 target 元素序号
        source_child_rel.update(SERIAL_NO=req.targetSerialNo)
    # source 元素移动至不同的父元素下
    else:
        # source 元素下方的同级元素序号 - 1（上移元素）
        TElementChildRel.filter(
            TElementChildRel.PARENT_NO == source_parent_no,
            TElementChildRel.SERIAL_NO > source_serial_no
        ).update({TElementChildRel.SERIAL_NO: TElementChildRel.SERIAL_NO - 1})
        # target 元素下方（包含 target 自身位置）的同级元素序号 + 1（下移元素）
        TElementChildRel.filter(
            TElementChildRel.PARENT_NO == req.targetParentNo,
            TElementChildRel.SERIAL_NO >= req.targetSerialNo
        ).update({TElementChildRel.SERIAL_NO: TElementChildRel.SERIAL_NO + 1})
        # 移动 source 元素至 target 位置
        source_child_rel.update(
            ROOT_NO=req.targetRootNo,
            PARENT_NO=req.targetParentNo,
            SERIAL_NO=req.targetSerialNo
        )

    # 校验 target 父级子代元素序号的连续性，避免埋坑
    target_child_rel_list = ElementChildRelDao.select_all_by_parent(req.targetParentNo)
    for index, target_child_rel in enumerate(target_child_rel_list):
        if target_child_rel.SERIAL_NO != index + 1:
            log.error(
                f'parentNo:[ {req.targetParentNo} ] '
                f'elementNo:[ {target_child_rel.CHILD_NO} ] '
                f'serialNo:[ {target_child_rel.SERIAL_NO} ]'
                f'序号连续性错误 '
            )
            raise ServiceError('Target 父级子代序号连续性有误')


@http_service
@transactional
def duplicate_element(req):
    # 查询元素
    source = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(source, '元素不存在')

    # 排除不支持复制的元素
    if source.ELEMENT_TYPE == ElementType.COLLECTION.value:
        raise ServiceError('暂不支持复制 Collection 元素')

    # 递归复制元素
    copied_no = copy_element(source, rename=True)
    # 下移 source 元素的下方的元素
    source_child_rel = ElementChildRelDao.select_by_child(source.ELEMENT_NO)
    TElementChildRel.filter(
        TElementChildRel.PARENT_NO == source_child_rel.PARENT_NO,
        TElementChildRel.SERIAL_NO > source_child_rel.SERIAL_NO
    ).update({TElementChildRel.SERIAL_NO: TElementChildRel.SERIAL_NO + 1})
    # 将 copy 元素插入 source 元素的下方
    TElementChildRel.insert(
        ROOT_NO=source_child_rel.ROOT_NO,
        PARENT_NO=source_child_rel.PARENT_NO,
        CHILD_NO=copied_no,
        SERIAL_NO=source_child_rel.SERIAL_NO + 1
    )
    return {'elementNo': copied_no}


@http_service
@transactional
def paste_element(req):
    # 查询 source 元素
    source = TestElementDao.select_by_no(req.sourceNo)
    check_is_not_blank(source, 'source元素不存在')

    # 查询 target 元素
    target = TestElementDao.select_by_no(req.targetNo)
    check_is_not_blank(target, 'target元素不存在')

    # 排除不支持剪贴的元素
    if source.ELEMENT_TYPE == ElementType.COLLECTION.value:
        raise ServiceError('暂不支持剪贴 Collection 元素')

    # 检查元素是否允许剪贴
    check_allow_to_paste(source, target)

    if req.pasteType == PasteType.COPY.value:
        paste_element_by_copy(source, target)
    else:
        paste_element_by_cut(source, target)


def check_allow_to_paste(source: TTestElement, target: TTestElement):
    # Group
    if is_group(source) and not is_collection(target):
        raise ServiceError(f'[ {source.ELEMENT_NAME} ]仅支持在[ 集合 ]下剪贴')
    # Sampler | Controller | Config
    elif (
        is_sampler(source) or is_controller(source) or is_config(source)
    ) and (
        is_test_collection(target) or not is_group(target) or not is_controller(target)
    ):
        raise ServiceError(f'[ {source.ELEMENT_NAME} ]仅支持在[ 片段、分组、控制器 ]下剪贴')
    # Timer
    elif is_timer(source) and (
        is_test_collection(target) or  # noqa
        not is_group(target) or  # noqa
        not is_sampler(target) or  # noqa
        not is_controller(target)  # noqa
    ):
        raise ServiceError(f'[ {source.ELEMENT_NAME} ]仅支持在[ 片段、分组、控制器、取样器 ]下剪贴')
    # Listener
    elif is_listener(source) and (not is_collection(target) or not is_group(target)):
        raise ServiceError(f'[ {source.ELEMENT_NAME} ]仅支持在[ 集合、片段、分组 ]下剪贴')
    # PreProcessor | PostProcessor | Assertion
    else:
        if not is_sampler(target):
            raise ServiceError(f'[ {source.ELEMENT_NAME} ]仅支持在[ 取样器 ]下剪贴')


def paste_element_by_copy(source: TTestElement, target: TTestElement):
    # 递归复制元素
    copied_no = copy_element(source, rename=True)
    # 查询 target 元素与父级元素关联
    target_child_rel = ElementChildRelDao.select_by_child(target.ELEMENT_NO)
    # 将 copy 元素插入 target 元素的最后
    TElementChildRel.insert(
        ROOT_NO=target_child_rel.ROOT_NO,
        PARENT_NO=target_child_rel.PARENT_NO,
        CHILD_NO=copied_no,
        SERIAL_NO=ElementChildRelDao.next_serial_number_by_parent(target_child_rel.PARENT_NO)
    )


def paste_element_by_cut(source: TTestElement, target: TTestElement):
    # 查询 source 元素与父级元素关联
    source_child_rel = ElementChildRelDao.select_by_child(source.ELEMENT_NO)
    # 上移 source 元素下方的元素
    TElementChildRel.filter(
        TElementChildRel.PARENT_NO == source_child_rel.PARENT_NO,
        TElementChildRel.SERIAL_NO > source_child_rel.SERIAL_NO
    ).update({
        TElementChildRel.SERIAL_NO: TElementChildRel.SERIAL_NO - 1
    })
    # 删除 source 父级关联
    source_child_rel.delete()
    # 查询 target 元素与父级元素关联
    target_child_rel = ElementChildRelDao.select_by_child(target.ELEMENT_NO)
    # 将 source 元素插入 target 元素的最后
    TElementChildRel.insert(
        ROOT_NO=target_child_rel.ROOT_NO,
        PARENT_NO=target_child_rel.PARENT_NO,
        CHILD_NO=source.ELEMENT_NO,
        SERIAL_NO=ElementChildRelDao.next_serial_number_by_parent(target_child_rel.PARENT_NO)
    )


def copy_element(source: TTestElement, rename=False):
    # 克隆元素和属性
    copied_no = clone_element(source, rename)
    # 遍历克隆元素子代
    source_child_rel_list = ElementChildRelDao.select_all_by_parent(source.ELEMENT_NO)
    for source_child_rel in source_child_rel_list:
        source_child = TestElementDao.select_by_no(source_child_rel.CHILD_NO)
        copied_child_no = copy_element(source_child)
        TElementChildRel.insert(
            ROOT_NO=source_child_rel.ROOT_NO,
            PARENT_NO=copied_no,
            CHILD_NO=copied_child_no,
            SERIAL_NO=source_child_rel.SERIAL_NO
        )
    # 遍历克隆内建元素
    source_builtin_rel_list = ElementBuiltinChildRelDao.select_all_by_parent(source.ELEMENT_NO)
    for source_builtin_rel in source_builtin_rel_list:
        source_builtin = TestElementDao.select_by_no(source_builtin_rel.CHILD_NO)
        copied_builtin_no = copy_element(source_builtin)
        TElementBuiltinChildRel.insert(
            ROOT_NO=source_builtin_rel.ROOT_NO,
            PARENT_NO=copied_no,
            CHILD_NO=copied_builtin_no,
            CHILD_TYPE=source_builtin_rel.CHILD_TYPE
        )
    return copied_no


def clone_element(source: TTestElement, rename=False):
    cloned_no = new_id()
    TTestElement.insert(
        ELEMENT_NO=cloned_no,
        ELEMENT_NAME=source.ELEMENT_NAME + ' copy' if rename else source.ELEMENT_NAME,
        ELEMENT_REMARK=source.ELEMENT_REMARK,
        ELEMENT_TYPE=source.ELEMENT_TYPE,
        ELEMENT_CLASS=source.ELEMENT_CLASS
    )
    props = ElementPropertyDao.select_all_by_element(source.ELEMENT_NO)
    for prop in props:
        TElementProperty.insert(
            ELEMENT_NO=cloned_no,
            PROPERTY_NAME=prop.PROPERTY_NAME,
            PROPERTY_VALUE=prop.PROPERTY_VALUE,
            PROPERTY_TYPE=prop.PROPERTY_TYPE
        )
    return cloned_no


@http_service
def query_element_http_headers_template_refs(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    # 查询所有关联的模板
    rels = HttpSamplerHeadersRelDao.select_all_by_sampler(req.elementNo)

    return [rel.TEMPLATE_NO for rel in rels]


@http_service
def create_element_http_headers_template_refs(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    for template_no in req.templateNumberList:
        # 查询模板
        template = HttpHeadersTemplateDao.select_by_no(template_no)
        if not template:
            continue

        # 添加模板关联
        THttpSamplerHeadersRel.insert(SAMPLER_NO=req.elementNo, TEMPLATE_NO=template_no)


@http_service
def modify_element_http_headers_template_refs(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    for template_no in req.templateNumberList:
        # 查询模板
        template = HttpHeadersTemplateDao.select_by_no(template_no)
        if not template:
            continue

        # 查询模板关联
        rel = HttpSamplerHeadersRelDao.select_by_sampler_and_template(req.elementNo, template_no)
        if rel:
            continue
        else:
            # 添加模板关联
            THttpSamplerHeadersRel.insert(
                SAMPLER_NO=req.elementNo,
                TEMPLATE_NO=template_no
            )

    # 删除不在请求中的模板
    HttpSamplerHeadersRelDao.delete_all_by_sampler_and_not_in_template(req.elementNo, req.templateNumberList)


@http_service
def query_element_builtins(req):
    result = []

    # 查询元素的内置元素关联
    builtin_rel_list = ElementBuiltinChildRelDao.select_all_by_parent(req.elementNo)
    if not builtin_rel_list:
        return result

    for rel in builtin_rel_list:
        # 查询内置元素
        builtin = TestElementDao.select_by_no(rel.CHILD_NO)
        if builtin:
            result.append({
                'elementNo': builtin.ELEMENT_NO,
                'elementName': builtin.ELEMENT_NAME,
                'elementType': builtin.ELEMENT_TYPE,
                'elementClass': builtin.ELEMENT_CLASS,
                'enabled': builtin.ENABLED,
                'property': query_element_property(builtin.ELEMENT_NO)
            })

    return result


@http_service
@transactional
def create_element_builtins(req):
    return add_element_builtins(root_no=req.rootNo, parent_no=req.parentNo, children=req.children)


def add_element_builtins(root_no, parent_no, children) -> List:
    result = []
    for child in children:
        # 查询父级元素
        parent = TestElementDao.select_by_no(parent_no)
        builtin_type = child.get('elementType')
        builtin_class = child.get('elementClass')

        # HTTPSampler 内置元素仅支持 Pre-Processor 和 Assertion
        if parent.ELEMENT_CLASS == ElementClass.HTTP_SAMPLER.value:
            if builtin_type not in [ElementType.PRE_PROCESSOR.value, ElementType.ASSERTION.value]:
                raise ServiceError('HTTPSampler 内置元素仅支持 Pre-Processor 和 Assertion')

        # 创建内置元素
        builtin_no = new_id()
        TTestElement.insert(
            ELEMENT_NO=builtin_no,
            ELEMENT_NAME=child.get('elementName'),
            ELEMENT_REMARK=child.get('elementRemark'),
            ELEMENT_TYPE=builtin_type,
            ELEMENT_CLASS=builtin_class,
            ENABLED=ElementStatus.ENABLE.value
        )

        # 创建内置元素属性
        properties = child.get('property', None)
        if properties:
            add_element_property(builtin_no, properties)

        # 创建内置元素关联
        TElementBuiltinChildRel.insert(
            ROOT_NO=root_no,
            PARENT_NO=parent_no,
            CHILD_NO=builtin_no,
            CHILD_TYPE=builtin_type
        )
        result.append(builtin_no)
    return result


@http_service
@transactional
def modify_element_builtins(req):
    update_element_builtins(req.list)


def update_element_builtins(children: Iterable[dict]):
    for child in children:
        # 内置元素编号
        builtin_no = child.get('elementNo')
        # 查询内置元素
        builtin = TestElementDao.select_by_no(builtin_no)
        check_is_not_blank(builtin, '内置元素不存在')

        # 更新内置元素
        builtin.update(ELEMENT_NAME=child.get('elementName'), ELEMENT_REMARK=child.get('elementRemark'))

        # 更新内置元素属性
        properties = child.get('property', None)
        if properties:
            update_element_property(builtin_no, properties)


def delete_element_builtin(element_no):
    # 查询内置元素
    element = TestElementDao.select_by_no(element_no)
    check_is_not_blank(element, '内置元素不存在')
    # 删除内置元素属性
    delete_element_property(element_no)
    # 删除内置元素
    element.delete()


def delete_element_builtins_by_parent(parent_no):
    # 根据父级删除所有内置元素
    builtin_rel_list = ElementBuiltinChildRelDao.select_all_by_parent(parent_no)
    if builtin_rel_list:
        for builtin_rel in builtin_rel_list:
            # 删除内置元素
            delete_element_builtin(builtin_rel.CHILD_NO)
            # 删除内置元素关联
            builtin_rel.delete()
