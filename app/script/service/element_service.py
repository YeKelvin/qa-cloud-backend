#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_service.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from typing import Iterable

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
    property = query_element_property(req.elementNo)

    # 查询元素是否有子代
    has_children = ElementChildRelDao.count_by_parent(req.elementNo) > 0

    return {
        'elementNo': element.ELEMENT_NO,
        'elementName': element.ELEMENT_NAME,
        'elementRemark': element.ELEMENT_REMARK,
        'elementType': element.ELEMENT_TYPE,
        'elementClass': element.ELEMENT_CLASS,
        'enabled': element.ENABLED,
        'property': property,
        'hasChildren': has_children
    }


def query_element_property(element_no):
    """查询元素属性"""
    property = {}
    props = ElementPropertyDao.select_all_by_element(element_no)
    for prop in props:
        if prop.PROPERTY_TYPE == 'DICT':
            property[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
        elif prop.PROPERTY_TYPE == 'LIST':
            property[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
        else:
            property[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE
    return property


@http_service
def query_element_children(req):
    return get_element_children(req.elementNo, req.depth)


@http_service
def query_elements_children(req):
    result = []
    for element_no in req.elementNumberList:
        element = TestElementDao.select_by_no(element_no)
        if not element:
            log.info(f'elementNo:[ {element_no} ] 元素不存在')
            continue
        children = get_element_children(element_no, req.depth)
        result.append({
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
    element_child_rel_list = ElementChildRelDao.select_all_by_parent(parent_no)
    if not element_child_rel_list:
        return result

    # 根据序号排序
    element_child_rel_list.sort(key=lambda k: k.SERIAL_NO)
    for rel in element_child_rel_list:
        # 查询子代元素
        element = TestElementDao.select_by_no(rel.CHILD_NO)
        if element:
            # 递归查询子代
            children = depth and get_element_children(rel.CHILD_NO, depth) or []
            result.append({
                'elementNo': element.ELEMENT_NO,
                'elementName': element.ELEMENT_NAME,
                'elementType': element.ELEMENT_TYPE,
                'elementClass': element.ELEMENT_CLASS,
                'enabled': element.ENABLED,
                'serialNo': rel.SERIAL_NO,
                'children': children
            })

    return result


@http_service
@transactional
def create_element(req):
    if (req.elementType == 'COLLECTION') and (not req.workspaceNo):
        raise ServiceError('新增测试集合时，工作空间编号不能为空')

    # 创建元素
    element_no = add_element(
        element_name=req.elementName,
        element_remark=req.elementRemark,
        element_type=req.elementType,
        element_class=req.elementClass,
        property=req.property,
        children=req.children
    )

    # 如果元素类型为 TestCollection 时，需要绑定 WorkspaceNo
    if req.workspaceNo:
        # 查询工作空间
        workspace = WorkspaceDao.select_by_no(req.workspaceNo)
        check_is_not_blank(workspace, '工作空间不存在')
        # 关联工作空间和测试集合
        TWorkspaceCollectionRel.insert(WORKSPACE_NO=req.workspaceNo, COLLECTION_NO=element_no)

    return {'elementNo': element_no}


def add_element(
    element_name, element_remark, element_type, element_class, property: dict = None, children: Iterable[dict] = None
):
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
    if property:
        add_element_property(element_no, property)

    # 创建元素子代
    if children:
        add_element_children(element_no, children)

    return element_no


@http_service
@transactional
def modify_element(req):
    update_element(
        element_no=req.elementNo,
        element_name=req.elementName,
        element_remark=req.elementRemark,
        property=req.property,
        children=req.children
    )


def update_element(element_no, element_name, element_remark, property: dict = None, children: Iterable[dict] = None):
    """递归修改元素"""
    # 查询元素
    element = TestElementDao.select_by_no(element_no)
    check_is_not_blank(element, '元素不存在')

    # 更新元素
    element.update(ELEMENT_NAME=element_name, ELEMENT_REMARK=element_remark)

    # 更新元素属性
    if property:
        update_element_property(element_no, property)

    # 更新元素子代
    if children:
        update_element_children(children)


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
    delete_element_builtin_by_parent(element_no)

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
        delete_element_builtin_by_parent(child_rel.CHILD_NO)
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
        TElementChildRel.query.filter(
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


def add_element_property(element_no, property: dict):
    """遍历添加元素属性"""
    for name, value in property.items():
        value_type = 'STR'

        if isinstance(value, dict):
            value_type = 'DICT'
            value = to_json(value)
        if isinstance(value, list):
            value_type = 'LIST'
            value = to_json(value)
        if isinstance(value, bytes):
            value = str(value, encoding='utf8')

        TElementProperty.insert(
            ELEMENT_NO=element_no, PROPERTY_NAME=name, PROPERTY_VALUE=value, PROPERTY_TYPE=value_type
        )


def update_element_property(element_no, property: dict):
    """遍历修改元素属性"""
    for name, value in property.items():
        # 查询元素属性
        prop = ElementPropertyDao.select_by_element_and_name(element_no, name)
        # 属性类型
        value_type = 'STR'
        # 更新元素属性值
        if isinstance(value, dict):
            value_type = 'DICT'
            value = to_json(value)
        if isinstance(value, list):
            value_type = 'LIST'
            value = to_json(value)
        if isinstance(value, bytes):
            value = str(value, encoding='utf8')

        prop.update(PROPERTY_VALUE=value, PROPERTY_TYPE=value_type)


@http_service
@transactional
def create_element_children(req):
    children = add_element_children(root_no=req.rootNo, parent_no=req.parentNo, children=req.children)
    return {'children': children}


def add_element_children(root_no, parent_no, children: Iterable[dict]):
    """添加元素子代"""
    result = []
    for child in children:
        # 新建子代元素
        child_no = add_element(
            element_name=child.get('elementName'),
            element_remark=child.get('elementRemark'),
            element_type=child.get('elementType'),
            element_class=child.get('elementClass'),
            property=child.get('property', None),
            children=child.get('children', None)
        )
        # 新建子代与父级关联
        TElementChildRel.insert(
            ROOT_NO=root_no,
            PARENT_NO=parent_no,
            CHILD_NO=child_no,
            SERIAL_NO=ElementChildRelDao.next_serialno_by_parent(parent_no)
        )
        # 新建子代内置元素
        builtin = child.get('builtIn', None)
        if builtin:
            add_element_builtin_children(parent_no=child_no, children=builtin, root_no=root_no)
        result.append(child_no)
    return result


@http_service
@transactional
def modify_element_children(req):
    update_element_children(children=req.children)


def update_element_children(children: Iterable[dict]):
    """遍历修改元素子代"""
    for child in children:
        child_no = child.get('elementNo', None)
        if not child_no:
            raise ServiceError('子代元素编号不能为空')

        update_element(
            element_no=child_no,
            element_name=child.get('elementName'),
            element_remark=child.get('elementRemark'),
            property=child.get('property', None),
            children=child.get('children', None)
        )


@http_service
@transactional
def move_up_element(req):
    # 查询元素子代关联
    child_rel = ElementChildRelDao.select_by_child(req.elementNo)
    check_is_not_blank(child_rel, '子元素不存在')

    # 父元素编号
    parent_no = child_rel.PARENT_NO

    # 统计子代个数
    children_count = ElementChildRelDao.count_by_parent(parent_no)
    serial_no = child_rel.SERIAL_NO

    # 如果元素只有一个子代或该子代元素排第一位则无需上移
    if children_count == 1 or serial_no == 1:
        return

    # 重新排序子元素
    upper_child_rel = ElementChildRelDao.select_by_parent_and_serialno(parent_no, serial_no - 1)
    upper_child_rel.update(SERIAL_NO=upper_child_rel.SERIAL_NO + 1)
    child_rel.update(SERIAL_NO=child_rel.SERIAL_NO - 1)


@http_service
@transactional
def move_down_element(req):
    # 查询元素子代关联
    child_rel = ElementChildRelDao.select_by_child(req.elementNo)
    check_is_not_blank(child_rel, '子元素不存在')

    # 父元素编号
    parent_no = child_rel.PARENT_NO

    # 统计子代个数
    children_count = ElementChildRelDao.count_by_parent(parent_no)
    serial_no = child_rel.SERIAL_NO

    # 如果元素只有一个子代或该子代元素排最后一位则无需下移
    if children_count == 1 or children_count == serial_no:
        return

    # 重新排序子元素
    lower_child_rel = ElementChildRelDao.select_by_parent_and_serialno(parent_no, serial_no + 1)
    lower_child_rel.update(SERIAL_NO=lower_child_rel.SERIAL_NO - 1)
    child_rel.update(SERIAL_NO=child_rel.SERIAL_NO + 1)


@http_service
@transactional
def move_element(req):
    # 查询 source 元素子代关联
    source_child_rel = ElementChildRelDao.select_by_child(req.sourceNo)
    check_is_not_blank(source_child_rel, 'source元素关联不存在')

    if req.targetSerialNo < 0:
        raise ServiceError('target元素序号不能小于0')
    if req.targetSerialNo == source_child_rel.SERIAL_NO:
        raise ServiceError('元素序号相等，无需移动元素')

    # source 父元素编号
    source_parent_no = source_child_rel.PARENT_NO
    # source 元素序号
    source_serial_no = source_child_rel.SERIAL_NO

    # 父元素不变时，仅重新排序 source 同级元素
    if source_parent_no == req.targetParentNo:
        # 元素移动类型，上移或下移 TODO:
        move_type = 'UP' if source_serial_no > req.targetSerialNo else 'DOWN'
        # source 同级且大于 target 元素序号的子元素序号 + 1（下移元素）
        ElementChildRelDao.plus_one_serialno_all_by_parent_and_greater_than_serialno(
            source_parent_no, req.targetSerialNo)
        # 更新 target 元素序号
        source_child_rel.update(SERIAL_NO=req.targetSerialNo)
    # source 元素移动至不同的父元素下
    else:
        # 删除 source 父级和 source 元素的关联
        source_child_rel.delete()
        # source 元素下方的同级元素序号 - 1（上移元素）
        ElementChildRelDao.minus_one_serialno_all_by_parent_and_greater_than_serialno(
            source_parent_no, source_serial_no)
        # target 元素下方的同级元素序号 + 1（下移元素）
        ElementChildRelDao.plus_one_serialno_all_by_parent_and_greater_than_serialno(
            req.targetParentNo, req.targetSerialNo)
        # 新增 target 父级和 target 元素的关联
        TElementChildRel.insert(
            ROOT_NO=req.targetRootNo,
            PARENT_NO=req.targetParentNo,
            CHILD_NO=req.sourceNo,
            SERIAL_NO=req.targetSerialNo
        )


@http_service
@transactional
def duplicate_element(req):
    # 查询元素
    source = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(source, '元素不存在')

    if source.ELEMENT_TYPE == 'COLLECTION' or source.ELEMENT_TYPE == 'GROUP':
        raise ServiceError('暂不支持复制Collection 或 Group')

    # 递归复制元素
    copied_no = copy_element(source, rename=True)
    # 将 copy 元素插入 source 元素的下方
    source_parent_rel = ElementChildRelDao.select_by_child(source.ELEMENT_NO)
    ElementChildRelDao.plus_one_serialno_all_by_parent_and_greater_than_serialno(
        source_parent_rel.PARENT_NO, source_parent_rel.SERIAL_NO
    )
    TElementChildRel.insert(
        ROOT_NO=source_parent_rel.ROOT_NO,
        PARENT_NO=source_parent_rel.PARENT_NO,
        CHILD_NO=copied_no,
        SERIAL_NO=source_parent_rel.SERIAL_NO + 1
    )
    return {'elementNo': copied_no}


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
    prop = ElementPropertyDao.select_by_element(source.ELEMENT_NO)
    TElementProperty.insert(
        ELEMENT_NO=cloned_no,
        PROPERTY_NAME=prop.PROPERTY_NAME,
        PROPERTY_VALUE=prop.PROPERTY_VALUE,
        PROPERTY_TYPE=prop.PROPERTY_TYPE
    )
    return cloned_no


@http_service
def query_element_http_headers_template_list(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    # 查询所有关联的模板
    rels = HttpSamplerHeadersRelDao.select_all_by_sampler(req.elementNo)

    return [rel.TEMPLATE_NO for rel in rels]


@http_service
def create_element_http_headers_template_list(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    for template_no in req.templateNoList:
        # 查询模板
        template = HttpHeadersTemplateDao.select_by_no(template_no)
        if not template:
            continue

        # 添加模板关联
        THttpSamplerHeadersRel.insert(SAMPLER_NO=req.elementNo, TEMPLATE_NO=template_no)


@http_service
def modify_element_http_headers_template_list(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    for template_no in req.templateNoList:
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
    HttpSamplerHeadersRelDao.delete_all_by_sampler_and_not_in_template(req.elementNo, req.templateNoList)


@http_service
def query_element_builtin_children(req):
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
def create_element_builtin_children(req):
    builtin = add_element_builtin_children(parent_no=req.parentNo, children=req.children, root_no=req.rootNo)
    return {'builtin': builtin}


def add_element_builtin_children(parent_no, children, root_no=None):
    result = []

    # 根据父级查询根元素编号
    if not root_no:
        parent_rel = ElementChildRelDao.select_by_child(parent_no)
        if parent_rel:
            root_no = parent_rel.ROOT_NO
        else:
            root_no = parent_no

    for builtin in children:
        # 查询父级元素
        parent = TestElementDao.select_by_no(parent_no)
        builtin_type = builtin.get('elementType')
        builtin_class = builtin.get('elementClass')

        # HTTPSampler 内置元素仅支持 Pre-Processor 和 Assertion
        if parent.ELEMENT_CLASS == ElementClass.HTTP_SAMPLER.value:
            if builtin_type not in [ElementType.PRE_PROCESSOR.value, ElementType.ASSERTION.value]:
                raise ServiceError('HTTPSampler 内置元素仅支持 Pre-Processor 和 Assertion')

        # 创建内置元素
        builtin_no = new_id()
        TTestElement.insert(
            ELEMENT_NO=builtin_no,
            ELEMENT_NAME=builtin.get('elementName'),
            ELEMENT_REMARK=builtin.get('elementRemark'),
            ELEMENT_TYPE=builtin_type,
            ELEMENT_CLASS=builtin_class,
            ENABLED=ElementStatus.ENABLE.value
        )

        # 创建内置元素属性
        property = builtin.get('property', None)
        if property:
            add_element_property(builtin_no, property)

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
def modify_element_builtin_children(req):
    update_element_builtin_children(req.children)


def update_element_builtin_children(children):
    for child in children:
        # 内置元素编号
        builtin_no = child.get('elementNo', None)
        if not builtin_no:
            raise ServiceError('内置元素编号不能为空')

        # 查询内置元素
        builtin = TestElementDao.select_by_no(builtin_no)
        check_is_not_blank(builtin, '内置元素不存在')

        # 更新内置元素
        builtin.update(ELEMENT_NAME=child.get('elementName'), ELEMENT_REMARK=child.get('elementRemark'))

        # 更新内置元素属性
        property = child.get('property', None)
        if property:
            update_element_property(builtin_no, property)


def delete_element_builtin(element_no):
    # 查询内置元素
    element = TestElementDao.select_by_no(element_no)
    check_is_not_blank(element, '内置元素不存在')
    # 删除内置元素属性
    delete_element_property(element_no)
    # 删除内置元素
    element.delete()


def delete_element_builtin_by_parent(parent_no):
    # 根据父级删除所有内置元素
    builtin_rel_list = ElementBuiltinChildRelDao.select_all_by_parent(parent_no)
    if builtin_rel_list:
        for builtin_rel in builtin_rel_list:
            # 删除内置元素
            delete_element_builtin(builtin_rel.CHILD_NO)
            # 删除内置元素关联
            builtin_rel.delete()
