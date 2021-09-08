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
from app.common.validator import check_is_blank
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
    conds.add_fuzzy_match(TTestElement.ELEMENT_NO, req.elementNo)
    conds.add_fuzzy_match(TTestElement.ELEMENT_NAME, req.elementName)
    conds.add_fuzzy_match(TTestElement.ELEMENT_REMARK, req.elementRemark)
    conds.add_fuzzy_match(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.add_fuzzy_match(TTestElement.ELEMENT_CLASS, req.elementClass)
    conds.add_fuzzy_match(TTestElement.ENABLED, req.enabled)

    if req.workspaceNo:
        conds.add_table(TWorkspaceCollectionRel)
        conds.add_exact_match(TWorkspaceCollectionRel.DECOLLECTION_NOL_STATE, TTestElement.ELEMENT_NO)
        conds.add_fuzzy_match(TWorkspaceCollectionRel.WORKSPACE_NO, req.workspaceNo)

    if req.workspaceName:
        conds.add_table(TWorkspace)
        conds.add_exact_match(TWorkspaceCollectionRel.DEL_STATE, 0)
        conds.add_exact_match(TWorkspaceCollectionRel.COLLECTION_NO, TTestElement.ELEMENT_NO)
        conds.add_exact_match(TWorkspaceCollectionRel.WORKSPACE_NO, TWorkspace.WORKSPACE_NO)
        conds.add_fuzzy_match(TWorkspace.WORKSPACE_NAME, req.workspaceName)

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
    conds.add_exact_match(TWorkspaceCollectionRel.COLLECTION_NO, TTestElement.ELEMENT_NO)
    conds.add_fuzzy_match(TWorkspaceCollectionRel.WORKSPACE_NO, req.workspaceNo)
    conds.add_fuzzy_match(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.add_fuzzy_match(TTestElement.ELEMENT_CLASS, req.elementClass)
    conds.add_fuzzy_match(TTestElement.ENABLED, req.enabled)

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


@http_service
def query_element_children(req):
    return get_element_children(req.elementNo, req.depth)


@http_service
def query_elements_children(req):
    result = []
    for element_no in req.elementNoList:
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

    # 根据child-order排序
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
        check_is_not_blank(workspace, '测试项目不存在')
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


@http_service
def create_element_property(req):
    # 查询元素属性
    el_prop = ElementPropertyDao.select_by_elementno_and_propname(req.elementNo, req.propertyName)
    check_is_blank(el_prop, '元素属性已存在')

    # 创建元素属性
    TElementProperty.insert(ELEMENT_NO=req.elementNo, PROPERTY_NAME=req.propertyName, PROPERTY_VALUE=req.propertyValue)


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

        TElementProperty.insert(
            ELEMENT_NO=element_no, PROPERTY_NAME=name, PROPERTY_VALUE=value, PROPERTY_TYPE=value_type
        )


@http_service
def modify_element_property(req):
    # 查询元素属性
    el_prop = ElementPropertyDao.select_by_elementno_and_propname(req.elementNo, req.propertyName)
    check_is_not_blank(el_prop, '元素属性不存在')

    # 更新元素属性值
    el_prop.update(property_value=req.propertyValue)


def update_element_property(element_no, property: dict):
    """遍历修改元素属性"""
    for name, value in property.items():
        # 查询元素属性
        prop = ElementPropertyDao.select_by_element_and_name(element_no, name)
        # 更新元素属性值
        if isinstance(value, str):
            prop.update(PROPERTY_VALUE=value, PROPERTY_TYPE='STR')
            continue
        if isinstance(value, dict):
            prop.update(PROPERTY_VALUE=to_json(value), PROPERTY_TYPE='DICT')
            continue
        if isinstance(value, list):
            prop.update(PROPERTY_VALUE=to_json(value), PROPERTY_TYPE='LIST')
            continue


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
            add_element_builtin_children(root_no, child_no, builtin)
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
def move_up_element_child(req):
    # 查询元素子代关联
    element_child_rel = ElementChildRelDao.select_by_child(req.childNo)
    check_is_not_blank(element_child_rel, '子元素不存在')

    # 父元素编号
    parent_no = element_child_rel.PARENT_NO

    # 统计子代个数
    children_count = ElementChildRelDao.count_by_parent(parent_no)
    serial_no = element_child_rel.SERIAL_NO

    # 如果元素只有一个子代或该子代元素排第一位则无需上移
    if children_count == 1 or serial_no == 1:
        return

    # 重新排序子元素
    upper_child_rel = ElementChildRelDao.select_by_parent_and_serialno(parent_no, serial_no - 1)
    upper_child_rel.update(SERIAL_NO=upper_child_rel.SERIAL_NO + 1)
    element_child_rel.update(SERIAL_NO=element_child_rel.SERIAL_NO - 1)


@http_service
@transactional
def move_down_element_child(req):
    # 查询元素子代关联
    element_child_rel = ElementChildRelDao.select_by_child(req.childNo)
    check_is_not_blank(element_child_rel, '子元素不存在')

    # 父元素编号
    parent_no = element_child_rel.PARENT_NO

    # 统计子代个数
    children_count = ElementChildRelDao.count_by_parent(parent_no)
    serial_no = element_child_rel.SERIAL_NO

    # 如果元素只有一个子代或该子代元素排最后一位则无需下移
    if children_count == 1 or children_count == serial_no:
        return

    # 重新排序子元素
    lower_child_rel = ElementChildRelDao.select_by_parent_and_serialno(parent_no, serial_no + 1)
    lower_child_rel.update(SERIAL_NO=lower_child_rel.SERIAL_NO - 1)
    element_child_rel.update(SERIAL_NO=element_child_rel.SERIAL_NO + 1)


@http_service
@transactional
def move_element_child(req):
    # TODO: 如果是跨集合移动元素，那么child-rel中的rootNo也要修改
    # 查询元素子代关联
    source_child_rel = ElementChildRelDao.select_by_child(req.sourceChildNo)
    check_is_not_blank(source_child_rel, '子元素不存在')

    # 当前父元素编号
    source_parent_no = source_child_rel.PARENT_NO

    # 父元素不变时，仅重新排序其他子元素
    if source_parent_no == req.targetParentNo:
        # 查询同级且大于目标元素序号的子元素关联
        other_child_rel_list = ElementChildRelDao.select_all_by_parent_and_greater_than_serialno(
            source_parent_no, req.targetSerialNo)
        # 同级且大于目标元素序号的子元素序号 + 1（下移元素）
        for rel in other_child_rel_list:
            rel.update(SERIAL_NO=rel.SERIAL_NO + 1)
        # 更新目标元素序号
        source_child_rel.update(SERIAL_NO=req.targetSerialNo)
    # 子元素移动至新的父元素下
    else:
        # 查询同级且大于目标元素序号的子元素关联
        source_parent_child_rel_list = ElementChildRelDao.select_all_by_parent_and_greater_than_serialno(
            source_parent_no, req.targetSerialNo)
        # 同级且大于目标元素序号的子元素序号 - 1（上移元素）
        for rel in source_parent_child_rel_list:
            rel.update(SERIAL_NO=rel.SERIAL_NO - 1)
        # 查询目标父级同级且大于目标元素序号的子元素关联
        target_parent_child_rel_list = ElementChildRelDao.select_all_by_parent_and_greater_than_serialno(
            req.targetParentNo, req.targetSerialNo)
        # 目标父级同级且大于目标元素序号的子元素序号 + 1（下移元素）
        for rel in target_parent_child_rel_list:
            rel.update(SERIAL_NO=rel.SERIAL_NO + 1)
        # 删除原父级和子元素的关联
        source_child_rel.delete()
        # 新建目标父级和子元素的关联
        TElementChildRel.insert(
            PARENT_NO=req.targetParentNo,
            CHILD_NO=req.sourceChildNo,
            SERIAL_NO=req.targetSerialNo
        )


@http_service
def duplicate_element(req):
    # 查询元素
    element = TestElementDao.select_by_no(req.elementNo)
    check_is_not_blank(element, '元素不存在')
    # TODO: 复制元素


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
                'property': query_element_property(builtin.ELEMENT_NO)
            })

    return result


@http_service
@transactional
def create_element_builtin_children(req):
    builtin = add_element_builtin_children(root_no=req.rootNo, parent_no=req.parentNo, children=req.children)
    return {'builtin': builtin}


def add_element_builtin_children(root_no, parent_no, children):
    result = []
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
