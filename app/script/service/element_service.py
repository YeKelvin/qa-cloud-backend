#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_service.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from typing import Iterable
from typing import List

from app.extension import db
from app.public.dao import workspace_dao as WorkspaceDao
from app.public.enum import WorkspaceScope
from app.public.model import TWorkspace
from app.public.model import TWorkspaceUser
from app.script.dao import element_builtin_children_dao as ElementBuiltinChildrenDao
from app.script.dao import element_children_dao as ElementChildrenDao
from app.script.dao import element_property_dao as ElementPropertyDao
from app.script.dao import http_header_template_dao as HttpHeaderTemplateDao
from app.script.dao import http_header_template_ref_dao as HttpHeaderTemplateRefDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.dao import workspace_collection_dao as WorkspaceCollectionDao
from app.script.enum import ElementClass
from app.script.enum import ElementStatus
from app.script.enum import ElementType
from app.script.enum import PasteType
from app.script.enum import is_assertion
from app.script.enum import is_collection
from app.script.enum import is_config
from app.script.enum import is_controller
from app.script.enum import is_group
from app.script.enum import is_http_sampler
from app.script.enum import is_listener
from app.script.enum import is_post_processor
from app.script.enum import is_pre_processor
from app.script.enum import is_sampler
from app.script.enum import is_snippet_collection
from app.script.enum import is_test_collection
from app.script.enum import is_timer
from app.script.model import TElementBuiltinChildren
from app.script.model import TElementChildren
from app.script.model import TElementProperty
from app.script.model import THttpHeaderTemplateRef
from app.script.model import TTestElement
from app.script.model import TWorkspaceCollection
from app.tools import globals
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.tools.validator import check_workspace_permission
from app.utils.json_util import from_json
from app.utils.json_util import to_json
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


def get_root_no(element_no):
    """根据元素编号获取根元素编号（集合编号）"""
    if not (link := ElementChildrenDao.select_by_child(element_no)):
        return element_no
    if not link.ROOT_NO:
        raise ServiceError(f'元素编号:[ {element_no} ] 根元素编号为空')
    return link.ROOT_NO


def get_workspace_no(collection_no) -> str:
    """获取元素空间编号"""
    workspace_collection = WorkspaceCollectionDao.select_by_collection(collection_no)
    if not workspace_collection:
        raise ServiceError('查询元素空间失败')
    return workspace_collection.WORKSPACE_NO


@http_service
def query_element_list(req):
    # 查询条件
    conds = QueryCondition(TTestElement)
    conds.like(TTestElement.ELEMENT_NO, req.elementNo)
    conds.like(TTestElement.ELEMENT_NAME, req.elementName)
    conds.like(TTestElement.ELEMENT_REMARK, req.elementRemark)
    conds.like(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.like(TTestElement.ELEMENT_CLASS, req.elementClass)
    conds.equal(TTestElement.ENABLED, req.enabled)

    if req.workspaceNo or req.workspaceName:
        conds.add_table(TWorkspaceCollection)

    if req.workspaceNo:
        conds.like(TWorkspaceCollection.WORKSPACE_NO, req.workspaceNo)
        conds.equal(TWorkspaceCollection.COLLECTION_NO, TTestElement.ELEMENT_NO)

    if req.workspaceName:
        conds.add_table(TWorkspace)
        conds.like(TWorkspace.WORKSPACE_NAME, req.workspaceName)
        conds.equal(TWorkspaceCollection.COLLECTION_NO, TTestElement.ELEMENT_NO)
        conds.equal(TWorkspaceCollection.WORKSPACE_NO, TWorkspace.WORKSPACE_NO)

    # TTestElement，TWorkspace，TWorkspaceCollection连表查询
    pagination = db.session.query(
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_REMARK,
        TTestElement.ELEMENT_TYPE,
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
    conds = QueryCondition(TTestElement, TWorkspaceCollection)
    conds.equal(TWorkspaceCollection.COLLECTION_NO, TTestElement.ELEMENT_NO)
    conds.equal(TWorkspaceCollection.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TTestElement.ENABLED, req.enabled)
    conds.equal(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.equal(TTestElement.ELEMENT_CLASS, req.elementClass)

    # TTestElement，TWorkspaceCollection连表查询
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
def query_element_all_in_private(req):
    # 公共空间条件查询
    public_conds = QueryCondition(TWorkspaceCollection, TWorkspace, TTestElement)
    public_conds.equal(TWorkspaceCollection.COLLECTION_NO, TTestElement.ELEMENT_NO)
    public_conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceCollection.WORKSPACE_NO)
    public_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PUBLIC.value)
    public_conds.equal(TTestElement.ENABLED, req.enabled)
    public_conds.equal(TTestElement.ELEMENT_TYPE, req.elementType)
    public_conds.equal(TTestElement.ELEMENT_CLASS, req.elementClass)
    public_filter = (
        db.session.query(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            TTestElement.ELEMENT_NO,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_REMARK,
            TTestElement.ELEMENT_TYPE,
            TTestElement.ELEMENT_CLASS,
            TTestElement.ENABLED
        )
        .filter(*public_conds)
    )

    # 保护空间条件查询
    protected_conds = QueryCondition(TWorkspaceCollection, TWorkspaceUser, TWorkspace, TTestElement)
    protected_conds.equal(TWorkspaceCollection.COLLECTION_NO, TTestElement.ELEMENT_NO)
    protected_conds.equal(TWorkspaceUser.USER_NO, globals.get_userno())
    protected_conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceCollection.WORKSPACE_NO)
    protected_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PROTECTED.value)
    protected_conds.equal(TTestElement.ENABLED, req.enabled)
    protected_conds.equal(TTestElement.ELEMENT_TYPE, req.elementType)
    protected_conds.equal(TTestElement.ELEMENT_CLASS, req.elementClass)
    protected_filter = (
        db.session.query(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            TTestElement.ELEMENT_NO,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_REMARK,
            TTestElement.ELEMENT_TYPE,
            TTestElement.ELEMENT_CLASS,
            TTestElement.ENABLED
        )
        .filter(*protected_conds)
    )

    # 私人空间条件查询
    private_conds = QueryCondition(TWorkspaceCollection, TWorkspaceUser, TWorkspace, TTestElement)
    private_conds.equal(TWorkspaceCollection.COLLECTION_NO, TTestElement.ELEMENT_NO)
    private_conds.equal(TWorkspaceUser.USER_NO, globals.get_userno())
    private_conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceCollection.WORKSPACE_NO)
    private_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PRIVATE.value)
    private_conds.equal(TTestElement.ENABLED, req.enabled)
    private_conds.equal(TTestElement.ELEMENT_TYPE, req.elementType)
    private_conds.equal(TTestElement.ELEMENT_CLASS, req.elementClass)
    private_filter = (
        db.session.query(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            TTestElement.ELEMENT_NO,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_REMARK,
            TTestElement.ELEMENT_TYPE,
            TTestElement.ELEMENT_CLASS,
            TTestElement.ENABLED
        )
        .filter(*private_conds)
    )

    items = (
        public_filter
        .union(protected_filter)
        .union(private_filter)
        .order_by(TWorkspace.WORKSPACE_SCOPE.desc())
        .all()
    )

    return [
        {
            'workspaceNo': item.WORKSPACE_NO,
            'workspaceName': item.WORKSPACE_NAME,
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'elementClass': item.ELEMENT_CLASS,
            'enabled': item.ENABLED
        }
        for item in items
    ]


@http_service
def query_element_all_with_children(req):
    # 查询条件
    conds = QueryCondition(TTestElement, TWorkspaceCollection)
    conds.equal(TWorkspaceCollection.COLLECTION_NO, TTestElement.ELEMENT_NO)
    conds.equal(TWorkspaceCollection.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TTestElement.ENABLED, req.enabled)
    conds.equal(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.equal(TTestElement.ELEMENT_CLASS, req.elementClass)

    # TTestElement，TWorkspaceCollection连表查询
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
        # 查询子代
        childconds = QueryCondition(TElementChildren, TTestElement)
        childconds.equal(TElementChildren.PARENT_NO, item.ELEMENT_NO)
        childconds.equal(TTestElement.ELEMENT_NO, TElementChildren.CHILD_NO)
        childconds.equal(TTestElement.ELEMENT_TYPE, req.childType)
        childconds.equal(TTestElement.ELEMENT_CLASS, req.childClass)
        childconds.equal(TTestElement.ENABLED, req.enabled)
        children = db.session.query(
            TElementChildren.SORT_NO,
            TTestElement.ELEMENT_NO,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_REMARK,
            TTestElement.ELEMENT_TYPE,
            TTestElement.ELEMENT_CLASS,
            TTestElement.ENABLED
        ).filter(*childconds).order_by(TElementChildren.SORT_NO).all()
        # 添加元素信息
        result.append({
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'elementClass': item.ELEMENT_CLASS,
            'enabled': item.ENABLED,
            'children': [
                {
                    'elementNo': child.ELEMENT_NO,
                    'elementName': child.ELEMENT_NAME,
                    'elementType': child.ELEMENT_TYPE,
                    'elementClass': child.ELEMENT_CLASS,
                    'enabled': child.ENABLED,
                    'children': []
                }
                for child in children
            ]
        })
    return result


@http_service
def query_element_info(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_exists(element, error_msg='元素不存在')

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
        if prop.PROPERTY_TYPE in ['DICT', 'LIST']:
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
    for element_no in req.elementNos:
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
    children_links = ElementChildrenDao.select_all_by_parent(parent_no)
    if not children_links:
        return result

    # 根据序号排序
    children_links.sort(key=lambda k: k.SORT_NO)
    for link in children_links:
        # 查询子代元素
        if element := TestElementDao.select_by_no(link.CHILD_NO):
            # 递归查询子代
            children = depth and get_element_children(link.CHILD_NO, depth) or []
            result.append({
                'rootNo': link.ROOT_NO,
                'elementNo': element.ELEMENT_NO,
                'elementName': element.ELEMENT_NAME,
                'elementType': element.ELEMENT_TYPE,
                'elementClass': element.ELEMENT_CLASS,
                'enabled': element.ENABLED,
                'sortNo': link.SORT_NO,
                'children': children
            })

    return result


@http_service
@transactional
def create_collection(req):
    # 校验工作空间
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')

    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 创建元素
    element_no = add_element(
        element_name=req.elementName,
        element_remark=req.elementRemark,
        element_type=req.elementType,
        element_class=req.elementClass,
        properties=req.property
    )

    # 新增空间元素关联
    TWorkspaceCollection.insert(WORKSPACE_NO=req.workspaceNo, COLLECTION_NO=element_no)

    return {'elementNo': element_no}


def add_element(element_name, element_remark, element_type, element_class, properties: dict = None):
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
    # 校验空间权限
    check_workspace_permission(get_workspace_no(req.rootNo))
    # 新增元素
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
        TElementChildren.insert(
            ROOT_NO=root_no,
            PARENT_NO=parent_no,
            CHILD_NO=child_no,
            SORT_NO=ElementChildrenDao.next_serial_number_by_parent(parent_no)
        )
        # 新建子代内置元素
        if builtin := child.get('builtIn', None):
            add_element_builtins(parent_no=child_no, children=builtin, root_no=root_no)
        result.append(child_no)
    return result


@http_service
@transactional
def modify_element(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))
    # 更新元素
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
        # 校验空间权限
        check_workspace_permission(get_workspace_no(get_root_no(item.elementNo)))
        # 更新元素
        update_element(
            element_no=item.elementNo,
            element_name=item.elementName,
            element_remark=item.elementRemark,
            properties=item.property
        )
        # 更新内置元素
        if item.builtIn:
            for builtin in item.builtIn:
                update_element_builtins(builtin)


def update_element(element_no, element_name, element_remark, properties: dict = None):
    # 查询元素
    element = TestElementDao.select_by_no(element_no)
    check_exists(element, error_msg='元素不存在')

    # 更新元素
    element.update(ELEMENT_NAME=element_name, ELEMENT_REMARK=element_remark)

    # 更新元素属性
    if properties:
        update_element_property(element_no, properties)


@http_service
@transactional
def remove_element(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))
    # 删除元素
    return delete_element(req.elementNo)


def delete_element(element_no):
    """递归删除元素"""
    # 查询元素
    element = TestElementDao.select_by_no(element_no)
    check_exists(element, error_msg='元素不存在')

    # 递归删除元素子代和子代关联
    delete_element_children(element_no)

    # 如果元素存在父级关联，则删除关联并重新排序子代元素
    delete_element_child(element_no)

    # 如果存在内置元素，一并删除
    delete_element_builtins_by_parent(element_no)

    # 删除元素属性
    delete_element_property(element_no)

    # 删除元素
    element.delete()


def delete_element_children(parent_no):
    """递归删除子代元素（包含子代元素、子代属性、子代与父级关联、子代内置元素和子代内置元素属性）"""
    # 查询所有子代关联列表
    children_links = ElementChildrenDao.select_all_by_parent(parent_no)
    for link in children_links:
        # 如果子代存在内置元素，一并删除
        delete_element_builtins_by_parent(link.CHILD_NO)
        # 查询子代元素
        child = TestElementDao.select_by_no(link.CHILD_NO)
        # 递归删除子代元素的子代和关联
        delete_element_children(link.CHILD_NO)
        # 删除子代元素属性
        delete_element_property(link.CHILD_NO)
        # 删除父子关联
        link.delete()
        # 删除子代元素
        child.delete()


def delete_element_child(child_no):
    # 如果子代存在父级关联，则删除关联并重新排序子代元素
    if link := ElementChildrenDao.select_by_child(child_no):
        # 重新排序父级子代
        TElementChildren.filter(
            TElementChildren.PARENT_NO == link.PARENT_NO, TElementChildren.SORT_NO > link.SORT_NO
        ).update(
            {TElementChildren.SORT_NO: TElementChildren.SORT_NO - 1}
        )
        # 删除父级关联
        link.delete()


def delete_element_property(element_no):
    # 查询所有元素属性
    props = ElementPropertyDao.select_all_by_element(element_no)
    for prop in props:
        prop.delete()


@http_service
@transactional
def enable_element(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_exists(element, error_msg='元素不存在')

    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))

    # 更新元素状态为启用
    element.update(ENABLED=ElementStatus.ENABLE.value)


@http_service
@transactional
def disable_element(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_exists(element, error_msg='元素不存在')

    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))

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
    source_link = ElementChildrenDao.select_by_child(req.sourceNo)
    check_exists(source_link, error_msg='source元素关联不存在')

    # 校验元素序号
    if req.targetSortNo < 0:
        raise ServiceError('target元素序号不能小于0')

    # source 父元素编号
    source_parent_no = source_link.PARENT_NO
    # source 元素序号
    source_sort_no = source_link.SORT_NO

    # 父元素不变时，仅重新排序 source 同级元素
    if source_parent_no == req.targetParentNo:
        # 校验空间权限
        check_workspace_permission(get_workspace_no(get_root_no(req.sourceNo)))
        # 序号相等时直接跳过
        if req.targetSortNo == source_link.SORT_NO:
            return
        # 元素移动类型，上移或下移
        move_type = 'UP' if source_sort_no > req.targetSortNo else 'DOWN'
        if move_type == 'UP':
            # 下移  [target, source) 区间元素
            TElementChildren.filter(
                TElementChildren.PARENT_NO == source_parent_no,
                TElementChildren.SORT_NO < source_sort_no,
                TElementChildren.SORT_NO >= req.targetSortNo
            ).update({TElementChildren.SORT_NO: TElementChildren.SORT_NO + 1})
        else:
            # 上移  (source, target] 区间元素
            TElementChildren.filter(
                TElementChildren.PARENT_NO == source_parent_no,
                TElementChildren.SORT_NO > source_sort_no,
                TElementChildren.SORT_NO <= req.targetSortNo,
            ).update({TElementChildren.SORT_NO: TElementChildren.SORT_NO - 1})
        # 更新 target 元素序号
        source_link.update(SORT_NO=req.targetSortNo)
    # source 元素移动至不同的父元素下
    else:
        # 校验空间权限
        check_workspace_permission(get_workspace_no(req.targetRootNo))
        # source 元素下方的同级元素序号 - 1（上移元素）
        TElementChildren.filter(
            TElementChildren.PARENT_NO == source_parent_no,
            TElementChildren.SORT_NO > source_sort_no
        ).update({TElementChildren.SORT_NO: TElementChildren.SORT_NO - 1})
        # target 元素下方（包含 target 自身位置）的同级元素序号 + 1（下移元素）
        TElementChildren.filter(
            TElementChildren.PARENT_NO == req.targetParentNo,
            TElementChildren.SORT_NO >= req.targetSortNo
        ).update({TElementChildren.SORT_NO: TElementChildren.SORT_NO + 1})
        # 移动 source 元素至 target 位置
        source_link.update(
            ROOT_NO=req.targetRootNo,
            PARENT_NO=req.targetParentNo,
            SORT_NO=req.targetSortNo
        )

    # 校验 target 父级子代元素序号的连续性，避免埋坑
    target_children_links = ElementChildrenDao.select_all_by_parent(req.targetParentNo)
    for index, target_link in enumerate(target_children_links):
        if target_link.SORT_NO != index + 1:
            log.error(
                f'parentNo:[ {req.targetParentNo} ] '
                f'elementNo:[ {target_link.CHILD_NO} ] '
                f'sortNo:[ {target_link.SORT_NO} ]'
                f'序号连续性错误 '
            )
            raise ServiceError('Target 父级子代序号连续性有误')


@http_service
@transactional
def duplicate_element(req):
    # 查询元素
    source = TestElementDao.select_by_no(req.elementNo)
    check_exists(source, error_msg='元素不存在')

    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))

    # 排除不支持复制的元素
    if source.ELEMENT_TYPE == ElementType.COLLECTION.value:
        raise ServiceError('暂不支持复制 Collection 元素')

    # 递归复制元素
    copied_no = copy_element(source, rename=True)
    # 下移 source 元素的下方的元素
    source_link = ElementChildrenDao.select_by_child(source.ELEMENT_NO)
    TElementChildren.filter(
        TElementChildren.PARENT_NO == source_link.PARENT_NO,
        TElementChildren.SORT_NO > source_link.SORT_NO
    ).update({TElementChildren.SORT_NO: TElementChildren.SORT_NO + 1})
    # 将 copy 元素插入 source 元素的下方
    TElementChildren.insert(
        ROOT_NO=source_link.ROOT_NO,
        PARENT_NO=source_link.PARENT_NO,
        CHILD_NO=copied_no,
        SORT_NO=source_link.SORT_NO + 1
    )
    return {'elementNo': copied_no}


@http_service
@transactional
def paste_element(req):
    # 查询 source 元素
    source = TestElementDao.select_by_no(req.sourceNo)
    check_exists(source, error_msg='source元素不存在')

    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.targetNo)))

    # 查询 target 元素
    target = TestElementDao.select_by_no(req.targetNo)
    check_exists(target, error_msg='target元素不存在')

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
        raise ServiceError('[分组] 仅支持在 [集合] 下剪贴')
    # Sampler
    elif is_sampler(source) and (
        is_test_collection(target) or not (is_snippet_collection(target) or is_group(target) or is_controller(target))
    ):
        raise ServiceError('[取样器] 仅支持在 [片段|分组|控制器] 下剪贴')
    # Controller
    elif is_controller(source) and (
        is_test_collection(target) or not (is_snippet_collection(target) or is_group(target) or is_controller(target))
    ):
        raise ServiceError('[控制器] 仅支持在 [片段|分组|控制器] 下剪贴')
    # Config
    elif is_config(source) and (
        is_test_collection(target) or not (is_group(target) or is_controller(target))
    ):
        raise ServiceError('[配置器] 仅支持在 [片段|分组|控制器] 下剪贴')
    # Timer
    elif is_timer(source) and (is_test_collection(target)
        or not (  # noqa
            is_snippet_collection(target) or is_group(target) or is_sampler(target) or is_controller(target)
        )  # noqa
    ):
        raise ServiceError('[时间控制器] 仅支持在 [ 片段|分组|控制器|取样器 ] 下剪贴')
    # Listener
    elif is_listener(source) and not(is_collection(target) or is_group(target)):
        raise ServiceError('[监听器] 仅支持在 [ 集合|片段|分组 ] 下剪贴')
    # PreProcessor
    elif is_pre_processor(source) and not is_sampler(target):
        raise ServiceError('[前置处理器] 仅支持在 [取样器] 下剪贴')
    # PostProcessor
    elif is_post_processor(source) and not is_sampler(target):
        raise ServiceError('[后置处理器] 仅支持在 [取样器] 下剪贴')
    # Assertion
    elif is_assertion(source) and not is_sampler(target):
        raise ServiceError('[断言器] 仅支持在 [取样器] 下剪贴')


def paste_element_by_copy(source: TTestElement, target: TTestElement):
    # 递归复制元素
    copied_no = copy_element(source, rename=True)
    # 将 copy 元素插入 target 元素的最后
    target_no = target.ELEMENT_NO
    TElementChildren.insert(
        ROOT_NO=get_root_no(target_no),
        PARENT_NO=target_no,
        CHILD_NO=copied_no,
        SORT_NO=ElementChildrenDao.next_serial_number_by_parent(target_no)
    )


def paste_element_by_cut(source: TTestElement, target: TTestElement):
    # 查询 source 元素与父级元素关联
    source_link = ElementChildrenDao.select_by_child(source.ELEMENT_NO)
    # 上移 source 元素下方的元素
    TElementChildren.filter(
        TElementChildren.PARENT_NO == source_link.PARENT_NO,
        TElementChildren.SORT_NO > source_link.SORT_NO
    ).update({
        TElementChildren.SORT_NO: TElementChildren.SORT_NO - 1
    })
    # 删除 source 父级关联
    source_link.delete()
    # 将 source 元素插入 target 元素的最后
    target_no = target.ELEMENT_NO
    TElementChildren.insert(
        ROOT_NO=get_root_no(target_no),
        PARENT_NO=target_no,
        CHILD_NO=source.ELEMENT_NO,
        SORT_NO=ElementChildrenDao.next_serial_number_by_parent(target_no)
    )


def copy_element(source: TTestElement, rename=False):
    # 克隆元素和属性
    copied_no = clone_element(source, rename)
    # 遍历克隆元素子代
    source_children_links = ElementChildrenDao.select_all_by_parent(source.ELEMENT_NO)
    for source_link in source_children_links:
        source_child = TestElementDao.select_by_no(source_link.CHILD_NO)
        copied_child_no = copy_element(source_child)
        TElementChildren.insert(
            ROOT_NO=source_link.ROOT_NO,
            PARENT_NO=copied_no,
            CHILD_NO=copied_child_no,
            SORT_NO=source_link.SORT_NO
        )
    # 遍历克隆内建元素
    source_builtin_links = ElementBuiltinChildrenDao.select_all_by_parent(source.ELEMENT_NO)
    for source_link in source_builtin_links:
        source_builtin = TestElementDao.select_by_no(source_link.CHILD_NO)
        copied_builtin_no = copy_element(source_builtin)
        TElementBuiltinChildren.insert(
            ROOT_NO=source_link.ROOT_NO,
            PARENT_NO=copied_no,
            CHILD_NO=copied_builtin_no,
            CHILD_TYPE=source_link.CHILD_TYPE
        )
    return copied_no


def clone_element(source: TTestElement, rename=False):
    cloned_no = new_id()
    # 克隆元素
    TTestElement.insert(
        ELEMENT_NO=cloned_no,
        ELEMENT_NAME=f'{source.ELEMENT_NAME} copy' if rename else source.ELEMENT_NAME,
        ELEMENT_REMARK=source.ELEMENT_REMARK,
        ELEMENT_TYPE=source.ELEMENT_TYPE,
        ELEMENT_CLASS=source.ELEMENT_CLASS
    )
    # 克隆元素属性
    props = ElementPropertyDao.select_all_by_element(source.ELEMENT_NO)
    for prop in props:
        TElementProperty.insert(
            ELEMENT_NO=cloned_no,
            PROPERTY_NAME=prop.PROPERTY_NAME,
            PROPERTY_VALUE=prop.PROPERTY_VALUE,
            PROPERTY_TYPE=prop.PROPERTY_TYPE
        )
    # 如果是 HTTPSampler ，克隆请求头模板
    if is_http_sampler(source):
        refs = HttpHeaderTemplateRefDao.select_all_by_sampler(source.ELEMENT_NO)
        for ref in refs:
            THttpHeaderTemplateRef.insert(SAMPLER_NO=cloned_no, TEMPLATE_NO=ref.TEMPLATE_NO)

    return cloned_no


@http_service
def query_element_httpheader_template_refs(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_exists(element, error_msg='元素不存在')

    # 查询所有关联的模板
    refs = HttpHeaderTemplateRefDao.select_all_by_sampler(req.elementNo)

    return [ref.TEMPLATE_NO for ref in refs]


@http_service
@transactional
def create_element_httpheader_template_refs(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_exists(element, error_msg='元素不存在')

    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))

    for template_no in req.templateNos:
        # 查询模板
        template = HttpHeaderTemplateDao.select_by_no(template_no)
        if not template:
            continue

        # 添加模板关联
        THttpHeaderTemplateRef.insert(SAMPLER_NO=req.elementNo, TEMPLATE_NO=template_no)


@http_service
@transactional
def modify_element_httpheader_template_refs(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_exists(element, error_msg='元素不存在')

    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))

    for template_no in req.templateNos:
        # 查询模板
        template = HttpHeaderTemplateDao.select_by_no(template_no)
        if not template:
            continue

        # 查询模板关联
        ref = HttpHeaderTemplateRefDao.select_by_sampler_and_template(req.elementNo, template_no)
        if not ref:
            # 添加模板关联
            THttpHeaderTemplateRef.insert(
                SAMPLER_NO=req.elementNo,
                TEMPLATE_NO=template_no
            )

    # 删除不在请求中的模板
    HttpHeaderTemplateRefDao.delete_all_by_sampler_and_notin_template(req.elementNo, req.templateNos)


@http_service
def query_element_builtins(req):
    result = []

    # 查询元素的内置元素关联
    builtin_links = ElementBuiltinChildrenDao.select_all_by_parent(req.elementNo)
    if not builtin_links:
        return result

    for link in builtin_links:
        # 查询内置元素
        if builtin := TestElementDao.select_by_no(link.CHILD_NO):
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
    # 校验空间权限
    check_workspace_permission(get_workspace_no(req.rootNo))
    # 新增内置元素
    return add_element_builtins(root_no=req.rootNo, parent_no=req.parentNo, children=req.children)


def add_element_builtins(root_no, parent_no, children) -> List:
    result = []
    for child in children:
        # 查询父级元素
        parent = TestElementDao.select_by_no(parent_no)
        builtin_type = child.get('elementType')
        builtin_class = child.get('elementClass')

        # HTTPSampler 内置元素仅支持 Pre-Processor 和 Assertion
        if (
                parent.ELEMENT_CLASS == ElementClass.HTTP_SAMPLER.value
                and builtin_type not in [ElementType.PRE_PROCESSOR.value, ElementType.ASSERTION.value]
        ):
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
        if properties := child.get('property', None):
            add_element_property(builtin_no, properties)

        # 创建内置元素关联
        TElementBuiltinChildren.insert(
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
    for builtin in req.list:
        # 校验空间权限
        check_workspace_permission(get_workspace_no(get_root_no(builtin.elementNo)))
        # 更新内置元素
        update_element_builtins(builtin)


def update_element_builtins(child):
    # 内置元素编号
    builtin_no = child.get('elementNo')
    # 查询内置元素
    builtin = TestElementDao.select_by_no(builtin_no)
    check_exists(builtin, error_msg='内置元素不存在')

    # 更新内置元素
    builtin.update(ELEMENT_NAME=child.get('elementName'), ELEMENT_REMARK=child.get('elementRemark'))

    # 更新内置元素属性
    if properties := child.get('property', None):
        update_element_property(builtin_no, properties)


def delete_element_builtin(element_no):
    # 查询内置元素
    element = TestElementDao.select_by_no(element_no)
    check_exists(element, error_msg='内置元素不存在')
    # 删除内置元素属性
    delete_element_property(element_no)
    # 删除内置元素
    element.delete()


def delete_element_builtins_by_parent(parent_no):
    # 根据父级删除所有内置元素
    if builtin_links := ElementBuiltinChildrenDao.select_all_by_parent(parent_no):
        for link in builtin_links:
            # 删除内置元素
            delete_element_builtin(link.CHILD_NO)
            # 删除内置元素关联
            link.delete()


@http_service
@transactional
def copy_collection_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 查询集合
    collection = TestElementDao.select_by_no(req.elementNo)
    if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
        raise ServiceError('仅支持复制集合')

    # 查询集合的空间
    workspace_collection = WorkspaceCollectionDao.select_by_collection(req.elementNo)
    if not workspace_collection:
        raise ServiceError('集合空间不存在')

    # 复制集合到指定的空间
    copied_no = copy_element(collection)
    TWorkspaceCollection.insert(WORKSPACE_NO=req.workspaceNo, COLLECTION_NO=copied_no)


@http_service
@transactional
def move_collection_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))  # 校验原空间权限
    check_workspace_permission(req.workspaceNo)  # 校验目标空间权限

    # 查询集合
    collection = TestElementDao.select_by_no(req.elementNo)
    if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
        raise ServiceError('仅运行移动集合')

    # 查询集合的空间
    workspace_collection = WorkspaceCollectionDao.select_by_collection(req.elementNo)
    if not workspace_collection:
        raise ServiceError('集合没有指定空间')

    # 移动空间
    workspace_collection.update(WORKSPACE_NO=req.workspaceNo)
