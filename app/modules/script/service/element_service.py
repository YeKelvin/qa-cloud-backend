#!/usr/bin/ python3
# @File    : element_service.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from loguru import logger

from app.database import db_query
from app.modules.public.dao import workspace_dao
from app.modules.public.model import TWorkspace
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import element_components_dao
from app.modules.script.dao import element_property_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.dao import workspace_collection_dao
from app.modules.script.dao import workspace_component_dao
from app.modules.script.enum import ElementStatus
from app.modules.script.enum import ElementType
from app.modules.script.enum import PasteType
from app.modules.script.enum import is_collection
from app.modules.script.enum import is_controller
from app.modules.script.enum import is_sampler
from app.modules.script.enum import is_snippet_collection
from app.modules.script.enum import is_test_collection
from app.modules.script.enum import is_timer
from app.modules.script.enum import is_worker
from app.modules.script.manager.element_manager import get_root_no
from app.modules.script.manager.element_manager import get_workspace_no
from app.modules.script.model import TElementChildren
from app.modules.script.model import TElementComponents
from app.modules.script.model import TElementProperty
from app.modules.script.model import TTestElement
from app.modules.script.model import TWorkspaceCollection
from app.modules.script.model import TWorkspaceComponent
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_workspace_permission
from app.utils.json_util import from_json
from app.utils.json_util import to_json
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_element_list(req):
    # 查询条件
    conds = QueryCondition(TTestElement)
    conds.like(TTestElement.ELEMENT_NO, req.elementNo)
    conds.like(TTestElement.ELEMENT_NAME, req.elementName)
    conds.like(TTestElement.ELEMENT_DESC, req.elementDesc)
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
    pagination = (
        db_query(
            TTestElement.ELEMENT_NO,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_DESC,
            TTestElement.ELEMENT_TYPE,
            TTestElement.ENABLED
        )
        .filter(*conds)
        .order_by(TTestElement.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'enabled': item.ENABLED
        }
        for item in pagination.items
    ]

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
    items = db_query(
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_DESC,
        TTestElement.ELEMENT_TYPE,
        TTestElement.ELEMENT_CLASS,
        TTestElement.ENABLED
    ).filter(*conds).order_by(TTestElement.CREATED_TIME.desc()).all()

    return [
        {
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
    items = db_query(
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_DESC,
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
        children = db_query(
            TElementChildren.CHILD_SORT,
            TTestElement.ELEMENT_NO,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_DESC,
            TTestElement.ELEMENT_TYPE,
            TTestElement.ELEMENT_CLASS,
            TTestElement.ENABLED
        ).filter(*childconds).order_by(TElementChildren.CHILD_SORT).all()
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
    element = test_element_dao.select_by_no(req.elementNo)
    check_exists(element, error_msg='元素不存在')

    # 查询元素属性
    properties = get_element_property(req.elementNo)

    return {
        'elementNo': element.ELEMENT_NO,
        'elementName': element.ELEMENT_NAME,
        'elementDesc': element.ELEMENT_DESC,
        'elementType': element.ELEMENT_TYPE,
        'elementClass': element.ELEMENT_CLASS,
        'elementAttrs': element.ELEMENT_ATTRS or {},
        'enabled': element.ENABLED,
        'property': properties
    }


def get_element_property(element_no):
    """查询元素属性"""
    properties = {}
    props = element_property_dao.select_all_by_element(element_no)
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
    for element_no in req.elements:
        element = test_element_dao.select_by_no(element_no)
        if not element:
            logger.warning(f'elementNo:[ {element_no} ] 元素不存在')
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
    # 查询元素所有子代
    relations = element_children_dao.select_all_by_parent(parent_no)
    if not relations:
        return result

    # 根据序号排序
    relations.sort(key=lambda k: k.CHILD_SORT)
    for relation in relations:
        # 查询子代元素
        if element := test_element_dao.select_by_no(relation.CHILD_NO):
            # 递归查询子代
            grandchildren = depth and get_element_children(element.ELEMENT_NO, depth) or []
            result.append({
                'rootNo': relation.ROOT_NO,
                'elementNo': element.ELEMENT_NO,
                'elementName': element.ELEMENT_NAME,
                'elementType': element.ELEMENT_TYPE,
                'elementClass': element.ELEMENT_CLASS,
                'elementIndex': relation.CHILD_SORT,
                'enabled': element.ENABLED,
                'children': grandchildren
            })

    return result


@http_service
def create_collection(req):
    # 校验工作空间
    workspace = workspace_dao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')

    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 创建元素
    element_no = add_element(
        element_name=req.elementName,
        element_desc=req.elementDesc,
        element_type=req.elementType,
        element_class=req.elementClass,
        element_attrs=req.elementAttrs,
        element_property=req.property
    )

    # 新建元素组件
    add_element_components(
        root_no=element_no,
        parent_no=element_no,
        components=req.componentList
    )

    # 新增空间元素关联
    TWorkspaceCollection.insert(WORKSPACE_NO=req.workspaceNo, COLLECTION_NO=element_no)

    return {'elementNo': element_no}


def add_element(
        element_name,
        element_desc,
        element_type,
        element_class,
        element_attrs: dict = None,
        element_property: dict = None
):
    # 创建元素
    element_no = new_id()
    TTestElement.insert(
        ELEMENT_NO=element_no,
        ELEMENT_NAME=element_name,
        ELEMENT_DESC=element_desc,
        ELEMENT_TYPE=element_type,
        ELEMENT_CLASS=element_class,
        ELEMENT_ATTRS=element_attrs,
        ENABLED=ElementStatus.ENABLE.value
    )
    # 创建元素属性
    add_element_property(element_no, element_property)
    return element_no


@http_service
def create_element_child(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(req.rootNo))
    # 新增元素
    element_no = add_element(
        element_name=req.elementName,
        element_desc=req.elementDesc,
        element_type=req.elementType,
        element_class=req.elementClass,
        element_attrs=req.elementAttrs,
        element_property=req.property
    )
    # 建立父子关联
    TElementChildren.insert(
        ROOT_NO=req.rootNo,
        PARENT_NO=req.parentNo,
        CHILD_NO=element_no,
        CHILD_SORT=element_children_dao.next_serial_number_by_parent(req.parentNo)
    )
    # 新建元素组件
    add_element_components(root_no=req.rootNo, parent_no=element_no, components=req.componentList)
    # 返回元素编号
    return {'elementNo': element_no}


@http_service
def modify_element(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))
    # 更新元素
    update_element(
        element_no=req.elementNo,
        element_name=req.elementName,
        element_desc=req.elementDesc,
        element_attrs=req.elementAttrs,
        element_property=req.property
    )
    # 更新元素组件
    update_element_components(
        parent_no=req.elementNo,
        component_list=req.componentList
    )


def update_element(
        element_no,
        element_name,
        element_desc,
        element_attrs: dict = None,
        element_property: dict = None
):
    # 查询元素
    element = test_element_dao.select_by_no(element_no)
    check_exists(element, error_msg='元素不存在')
    # 更新元素
    element.update(
        ELEMENT_NAME=element_name,
        ELEMENT_DESC=element_desc,
        ELEMENT_ATTRS=element_attrs
    )
    # 更新元素属性
    update_element_property(element_no, element_property)


@http_service
def remove_element(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))
    # 删除元素
    return delete_element(req.elementNo)


def delete_element(element_no):
    """递归删除元素"""
    # 查询元素
    element = test_element_dao.select_by_no(element_no)
    check_exists(element, error_msg='元素不存在')

    # 递归删除元素子代和子代关联
    delete_element_children(element_no)

    # 如果元素存在父级关联，则删除关联并重新排序子代元素
    delete_element_child(element_no)

    # 如果存在元素组件，一并删除
    delete_element_components_by_parent(element_no)

    # 删除元素属性
    delete_element_property(element_no)

    # 删除元素
    element.delete()


def delete_element_children(parent_no):
    """递归删除子代元素（包含子代元素、子代属性、子代与父级关联、元素组件和元素组件属性）"""
    # 查询所有子代关联列表
    children_relations = element_children_dao.select_all_by_parent(parent_no)
    for relation in children_relations:
        # 如果子代存在元素组件，一并删除
        delete_element_components_by_parent(relation.CHILD_NO)
        # 查询子代元素
        child = test_element_dao.select_by_no(relation.CHILD_NO)
        # 递归删除子代元素的子代和关联
        delete_element_children(relation.CHILD_NO)
        # 删除子代元素属性
        delete_element_property(relation.CHILD_NO)
        # 删除父子关联
        relation.delete()
        # 删除子代元素
        child.delete()


def delete_element_child(child_no):
    # 如果子代存在父级关联，则删除关联并重新排序子代元素
    if relation := element_children_dao.select_by_child(child_no):
        # 重新排序父级子代
        TElementChildren.filter(
            TElementChildren.PARENT_NO == relation.PARENT_NO, TElementChildren.CHILD_SORT > relation.CHILD_SORT
        ).update(
            {TElementChildren.CHILD_SORT: TElementChildren.CHILD_SORT - 1}
        )
        # 删除父级关联
        relation.delete()


def delete_element_property(element_no):
    # 查询所有元素属性
    props = element_property_dao.select_all_by_element(element_no)
    for prop in props:
        prop.delete()


@http_service
def enable_element(req):
    # 查询元素
    element = test_element_dao.select_by_no(req.elementNo)
    check_exists(element, error_msg='元素不存在')

    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))

    # 更新元素状态为启用
    element.update(ENABLED=ElementStatus.ENABLE.value)


@http_service
def disable_element(req):
    # 查询元素
    element = test_element_dao.select_by_no(req.elementNo)
    check_exists(element, error_msg='元素不存在')

    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))

    # 更新元素状态为禁用
    element.update(ENABLED=ElementStatus.DISABLE.value)


@http_service
def toggle_element_state(req):
    # 查询元素
    element = test_element_dao.select_by_no(req.elementNo)
    check_exists(element, error_msg='元素不存在')
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))
    # 更新元素状态
    state = ElementStatus.DISABLE.value if element.ENABLED == ElementStatus.ENABLE.value else ElementStatus.ENABLE.value
    element.update(ENABLED=state)


def add_element_property(element_no, element_property: dict):
    """遍历添加元素属性"""
    if element_property is None:
        return
    for name, value in element_property.items():
        property_type = 'STR'
        if isinstance(value, dict):
            property_type = 'DICT'
            value = to_json(value)
        if isinstance(value, list):
            property_type = 'LIST'
            value = to_json(value)

        TElementProperty.insert(
            ELEMENT_NO=element_no,
            PROPERTY_NAME=name,
            PROPERTY_VALUE=value,
            PROPERTY_TYPE=property_type
        )


def update_element_property(element_no, element_property: dict):
    """遍历修改元素属性"""
    if element_property is None:
        return
    # 遍历更新元素属性
    for name, value in element_property.items():
        # 查询元素属性
        prop = element_property_dao.select_by_element_and_name(element_no, name)
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
    element_property_dao.delete_all_by_element_and_notin_name(element_no, list(element_property.keys()))


@http_service
def move_element(req):
    # 查询 source 元素上级关联
    source_upper_relation = element_children_dao.select_by_child(req.sourceNo)
    check_exists(source_upper_relation, error_msg='source元素上级关联不存在')

    # 校验元素序号
    if req.targetIndex < 0:
        raise ServiceError('target元素序号不能小于0')

    # source 父元素编号
    source_parent_no = source_upper_relation.PARENT_NO
    # source 元素序号
    source_index = source_upper_relation.CHILD_SORT

    # 父元素不变时，仅重新排序 source 同级元素
    if source_parent_no == req.targetParentNo:
        # 校验空间权限
        check_workspace_permission(get_workspace_no(get_root_no(req.sourceNo)))
        # 序号相等时直接跳过
        if req.targetIndex == source_upper_relation.CHILD_SORT:
            return
        # 元素移动类型，上移或下移
        move_type = 'UP' if source_index > req.targetIndex else 'DOWN'
        if move_type == 'UP':
            # 下移  [target, source) 区间元素
            TElementChildren.filter(
                TElementChildren.PARENT_NO == source_parent_no,
                TElementChildren.CHILD_SORT < source_index,
                TElementChildren.CHILD_SORT >= req.targetIndex
            ).update({TElementChildren.CHILD_SORT: TElementChildren.CHILD_SORT + 1})
        else:
            # 上移  (source, target] 区间元素
            TElementChildren.filter(
                TElementChildren.PARENT_NO == source_parent_no,
                TElementChildren.CHILD_SORT > source_index,
                TElementChildren.CHILD_SORT <= req.targetIndex,
            ).update({TElementChildren.CHILD_SORT: TElementChildren.CHILD_SORT - 1})
        # 更新 target 元素序号
        source_upper_relation.update(CHILD_SORT=req.targetIndex)
    # source 元素移动至不同的父元素下
    else:
        # 校验空间权限
        check_workspace_permission(get_workspace_no(req.targetRootNo))
        # source 元素下方的同级元素序号 - 1（上移元素）
        TElementChildren.filter(
            TElementChildren.PARENT_NO == source_parent_no,
            TElementChildren.CHILD_SORT > source_index
        ).update({TElementChildren.CHILD_SORT: TElementChildren.CHILD_SORT - 1})
        # target 元素下方（包含 target 自身位置）的同级元素序号 + 1（下移元素）
        TElementChildren.filter(
            TElementChildren.PARENT_NO == req.targetParentNo,
            TElementChildren.CHILD_SORT >= req.targetIndex
        ).update({TElementChildren.CHILD_SORT: TElementChildren.CHILD_SORT + 1})
        # 移动 source 元素至 target 位置
        source_upper_relation.update(
            ROOT_NO=req.targetRootNo,
            PARENT_NO=req.targetParentNo,
            CHILD_SORT=req.targetIndex
        )
        # 递归修改 source 子代元素的根元素编号
        update_children_root(req.sourceNo, req.targetRootNo)

    # 校验 target 父级子代元素序号的连续性，避免埋坑
    target_children_relations = element_children_dao.select_all_by_parent(req.targetParentNo)
    for index, target_relation in enumerate(target_children_relations):
        if target_relation.CHILD_SORT != index + 1:
            logger.error(
                f'父级编号:[ {req.targetParentNo} ] '
                f'元素编号:[ {target_relation.CHILD_NO} ] '
                f'序号:[ {target_relation.CHILD_SORT} ]'
                f'序号连续性错误 '
            )
            raise ServiceError('Target 父级子代序号连续性有误')


def update_children_root(parent_no, root_no):
    """递归修改子代元素的根元素编号"""
    # 查询子代关联
    lower_relation_list = element_children_dao.select_all_by_parent(parent_no)
    if not lower_relation_list:
        return
    # 遍历更新根元素编号
    for relation in lower_relation_list:
        relation.update(ROOT_NO=root_no)
        # 递归修改
        update_children_root(relation.CHILD_NO, root_no)

@http_service
def duplicate_element(req):
    # 查询元素
    source = test_element_dao.select_by_no(req.elementNo)
    check_exists(source, error_msg='元素不存在')

    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))

    # 排除不支持复制的元素
    if source.ELEMENT_TYPE == ElementType.COLLECTION.value:
        raise ServiceError('暂不支持复制集合')

    # 递归复制元素
    copied_no = copy_element(source)
    # 下移 source 元素的下方的元素
    source_upper_relation = element_children_dao.select_by_child(source.ELEMENT_NO)
    TElementChildren.filter(
        TElementChildren.PARENT_NO == source_upper_relation.PARENT_NO,
        TElementChildren.CHILD_SORT > source_upper_relation.CHILD_SORT
    ).update({TElementChildren.CHILD_SORT: TElementChildren.CHILD_SORT + 1})
    # 将 copy 元素插入 source 元素的下方
    TElementChildren.insert(
        ROOT_NO=source_upper_relation.ROOT_NO,
        PARENT_NO=source_upper_relation.PARENT_NO,
        CHILD_NO=copied_no,
        CHILD_SORT=source_upper_relation.CHILD_SORT + 1
    )
    return {'elementNo': copied_no}


@http_service
def paste_element(req):
    # 查询 source 元素
    source = test_element_dao.select_by_no(req.sourceNo)
    check_exists(source, error_msg='source元素不存在')

    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.targetNo)))

    # 查询 target 元素
    target = test_element_dao.select_by_no(req.targetNo)
    check_exists(target, error_msg='target元素不存在')

    # 排除不支持剪贴的元素
    if source.ELEMENT_TYPE == ElementType.COLLECTION.value:
        raise ServiceError('暂不支持剪贴集合')

    # 检查元素是否允许剪贴
    check_allow_to_paste(source, target)

    if req.pasteType == PasteType.COPY.value:
        paste_element_by_copy(source, target)
    elif req.pasteType == PasteType.CUT.value:
        paste_element_by_cut(source, target)
    else:
        raise ServiceError('剪贴类型非法')

def check_allow_to_paste(source: TTestElement, target: TTestElement):
    # Wroup
    if is_worker(source) and not is_collection(target):
        raise ServiceError('[用例] 仅支持在 [集合] 节点下剪贴')
    # Sampler
    elif is_sampler(source) and (
        is_test_collection(target) or not (is_snippet_collection(target) or is_worker(target) or is_controller(target))
    ):
        raise ServiceError('[请求] 仅支持在 [片段|用例|逻辑控制器] 节点下剪贴')
    # Controller
    elif is_controller(source) and (
        is_test_collection(target) or not (is_snippet_collection(target) or is_worker(target) or is_controller(target))
    ):
        raise ServiceError('[逻辑控制器] 仅支持在 [片段|用例|逻辑控制器] 节点下剪贴')
    # Timer
    elif is_timer(source) and (is_test_collection(target)
        or not (  # noqa
            is_snippet_collection(target) or is_worker(target) or is_sampler(target) or is_controller(target)
        )  # noqa
    ):
        raise ServiceError('[时间控制器] 仅支持在 [ 片段|用例|逻辑控制器 ] 节点下剪贴')


def paste_element_by_copy(source: TTestElement, target: TTestElement):
    target_no = target.ELEMENT_NO
    target_root_no = get_root_no(target_no)
    # 递归复制元素
    copied_no = copy_element(source, root_no=target_root_no)
    # 将 copy 元素插入 target 元素的最后
    TElementChildren.insert(
        ROOT_NO=target_root_no,
        PARENT_NO=target_no,
        CHILD_NO=copied_no,
        CHILD_SORT=element_children_dao.next_serial_number_by_parent(target_no)
    )


def paste_element_by_cut(source: TTestElement, target: TTestElement):
    source_no = source.ELEMENT_NO
    target_no = target.ELEMENT_NO
    target_root_no = get_root_no(target_no)
    # 查询 source 元素与父级元素关联
    source_upper_relation = element_children_dao.select_by_child(source_no)
    # 上移 source 元素下方的元素
    TElementChildren.filter(
        TElementChildren.PARENT_NO == source_upper_relation.PARENT_NO,
        TElementChildren.CHILD_SORT > source_upper_relation.CHILD_SORT
    ).update({
        TElementChildren.CHILD_SORT: TElementChildren.CHILD_SORT - 1
    })
    # 修改 source 上级关联
    source_upper_relation.update(
        ROOT_NO=target_root_no,
        PARENT_NO=target_no,
        CHILD_SORT=element_children_dao.next_serial_number_by_parent(target_no)
    )
    # 递归修改 source 子代元素的根元素编号
    update_children_root(source_no, target_root_no)


def copy_element(source: TTestElement, rename=False, root_no=None):
    # 克隆元素和属性
    copied_no = clone_element(source, rename)
    # 遍历克隆元素子代
    source_children_relations = element_children_dao.select_all_by_parent(source.ELEMENT_NO)
    for source_relation in source_children_relations:
        source_child = test_element_dao.select_by_no(source_relation.CHILD_NO)
        copied_child_no = copy_element(source_child)
        TElementChildren.insert(
            ROOT_NO=root_no or source_relation.ROOT_NO,
            PARENT_NO=copied_no,
            CHILD_NO=copied_child_no,
            CHILD_SORT=source_relation.CHILD_SORT
        )
    # 遍历克隆内建元素
    source_component_relations = element_components_dao.select_all_by_parent(source.ELEMENT_NO)
    for source_relation in source_component_relations:
        source_component = test_element_dao.select_by_no(source_relation.CHILD_NO)
        copied_component_no = copy_element(source_component)
        TElementComponents.insert(
            ROOT_NO=source_relation.ROOT_NO,
            PARENT_NO=copied_no,
            CHILD_NO=copied_component_no,
            CHILD_TYPE=source_relation.CHILD_TYPE,
            CHILD_SORT=source_relation.CHILD_SORT
        )
    return copied_no


def clone_element(source: TTestElement, rename=False):
    cloned_no = new_id()
    # 克隆元素
    TTestElement.insert(
        ELEMENT_NO=cloned_no,
        ELEMENT_NAME=f'{source.ELEMENT_NAME} copy' if rename else source.ELEMENT_NAME,
        ELEMENT_DESC=source.ELEMENT_DESC,
        ELEMENT_TYPE=source.ELEMENT_TYPE,
        ELEMENT_CLASS=source.ELEMENT_CLASS,
        ELEMENT_ATTRS=source.ELEMENT_ATTRS
    )
    # 克隆元素属性
    props = element_property_dao.select_all_by_element(source.ELEMENT_NO)
    for prop in props:
        TElementProperty.insert(
            ELEMENT_NO=cloned_no,
            PROPERTY_NAME=prop.PROPERTY_NAME,
            PROPERTY_VALUE=prop.PROPERTY_VALUE,
            PROPERTY_TYPE=prop.PROPERTY_TYPE
        )

    return cloned_no


@http_service
def query_element_components(req):
    result = []

    # 查询元素组件关联
    relations = element_components_dao.select_all_by_parent(req.elementNo)
    if not relations:
        return result

    for relation in relations:
        # 查询元素组件
        if component := test_element_dao.select_by_no(relation.CHILD_NO):
            result.append({
                'elementNo': component.ELEMENT_NO,
                'elementName': component.ELEMENT_NAME,
                'elementType': component.ELEMENT_TYPE,
                'elementClass': component.ELEMENT_CLASS,
                'elementIndex': relation.CHILD_SORT,
                'property': get_element_property(component.ELEMENT_NO),
                'enabled': component.ENABLED
            })

    return result


def add_element_components(root_no, parent_no, components) -> list:
    result = []
    if components is None:
        return result
    for component in components:
        component_no = add_element_component(root_no, parent_no, component)
        result.append(component_no)
    return result


def add_element_component(root_no, parent_no, component):
    # 创建元素
    component_no = new_id()
    TTestElement.insert(
        ELEMENT_NO=component_no,
        ELEMENT_NAME=component.get('elementName'),
        ELEMENT_DESC=component.get('elementDesc', None),
        ELEMENT_TYPE=component.get('elementType'),
        ELEMENT_CLASS=component.get('elementClass'),
        ENABLED=component.get('enabled', ElementStatus.ENABLE.value)
    )
    # 创建元素属性
    add_element_property(component_no, component.get('property', None))
    # 创建元素关联
    TElementComponents.insert(
        ROOT_NO=root_no,
        PARENT_NO=parent_no,
        CHILD_NO=component_no,
        CHILD_TYPE=component.get('elementType'),
        CHILD_SORT=component.get('elementIndex', 0)
    )
    return component_no


def update_element_component(element_no, element_name, element_desc, element_property=None, enabled: bool = None):
    # 查询元素
    component = test_element_dao.select_by_no(element_no)
    check_exists(component, error_msg='元素不存在')
    # 更新元素
    if enabled is not None:
        component.update(
            ELEMENT_NAME=element_name,
            ELEMENT_DESC=element_desc,
            ENABLED=enabled
        )
    else:
        component.update(
            ELEMENT_NAME=element_name,
            ELEMENT_DESC=element_desc
        )
    # 更新元素属性
    update_element_property(element_no, element_property)


def update_element_components(parent_no: str, component_list: list):
    # 临时存储元素编号，用于删除非请求中的元素
    if component_list is None:
        return
    components = []
    for component in component_list:
        # 元素存在则更新
        if element := test_element_dao.select_by_no(component.elementNo):
            # 存储元素的编号
            components.append(component.elementNo)
            # 更新元素
            element.update(
                ELEMENT_NAME=component.elementName,
                ELEMENT_DESC=component.get('elementDesc', None),
                ENABLED=component.enabled
            )
            # 更新元素属性
            update_element_property(component.elementNo, component.get('property', None))
            # 更新序号
            relation = element_components_dao.select_by_child(component.elementNo)
            relation.update(CHILD_SORT=component.elementIndex)
        # 元素不存在则新增
        else:
            # 新增元素组件
            component_no = add_element_component(get_root_no(parent_no), parent_no, component)
            # 存储元素组件的编号
            components.append(component_no)

    # 移除非请求中元素组件
    TElementComponents.deletes(
        TElementComponents.PARENT_NO == parent_no,
        TElementComponents.CHILD_TYPE.in_([
            ElementType.CONFIG.value,
            ElementType.PREV_PROCESSOR.value,
            ElementType.POST_PROCESSOR.value,
            ElementType.ASSERTION.value
        ]),
        TElementComponents.CHILD_NO.notin_(components),
    )


def delete_element_component(element_no):
    # 查询元素
    element = test_element_dao.select_by_no(element_no)
    check_exists(element, error_msg='元素不存在')
    # 删除元素属性
    delete_element_property(element_no)
    # 删除元素
    element.delete()


def delete_element_components_by_parent(parent_no):
    # 根据父级删除所有元素组件
    if relations := element_components_dao.select_all_by_parent(parent_no):
        for relation in relations:
            # 删除元素组件
            delete_element_component(relation.CHILD_NO)
            # 删除元素组件关联
            relation.delete()


@http_service
def copy_collection_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 查询集合
    collection = test_element_dao.select_by_no(req.elementNo)
    if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
        raise ServiceError('仅支持复制集合')

    # 查询集合的空间
    workspace_collection = workspace_collection_dao.select_by_collection(req.elementNo)
    if not workspace_collection:
        raise ServiceError('集合空间不存在')

    # 复制集合到指定的空间
    copied_no = copy_element(collection)
    TWorkspaceCollection.insert(WORKSPACE_NO=req.workspaceNo, COLLECTION_NO=copied_no)


@http_service
def move_collection_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))  # 校验原空间权限
    check_workspace_permission(req.workspaceNo)  # 校验目标空间权限

    # 查询集合
    collection = test_element_dao.select_by_no(req.elementNo)
    if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
        raise ServiceError('仅运行移动集合')

    # 查询集合的空间
    if workspace_collection := workspace_collection_dao.select_by_collection(req.elementNo):
        # 移动空间
        workspace_collection.update(WORKSPACE_NO=req.workspaceNo)
    else:
        raise ServiceError('集合没有指定空间')


@http_service
def query_workspace_components(req):
    result = []

    # 查询空间的所有组件
    workspace_component_list = workspace_component_dao.select_all_by_workspace(req.workspaceNo)
    if not workspace_component_list:
        return result

    for workspace_component in workspace_component_list:
        # 查询元素
        if element := test_element_dao.select_by_no(workspace_component.COMPONENT_NO):
            result.append({
                'elementNo': element.ELEMENT_NO,
                'elementName': element.ELEMENT_NAME,
                'elementType': element.ELEMENT_TYPE,
                'elementClass': element.ELEMENT_CLASS,
                'elementIndex': workspace_component.COMPONENT_SORT,
                'property': get_element_property(element.ELEMENT_NO),
                'enabled': element.ENABLED
            })

    return result


@http_service
def set_workspace_components(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)
    # 遍历处理组件
    components = []
    for component in req.componentList:
        # 组件元素存在则更新
        if element := test_element_dao.select_by_no(component.elementNo):
            # 存储元素的编号
            components.append(component.elementNo)
            # 更新元素
            element.update(
                ELEMENT_NAME=component.elementName,
                ELEMENT_DESC=component.get('elementDesc', None),
                ENABLED=component.enabled
            )
            # 更新元素属性
            update_element_property(component.elementNo, component.get('property', None))
            # 更新序号
            workspace_component = workspace_component_dao.select_by_component(component.elementNo)
            workspace_component.update(COMPONENT_SORT=component.elementIndex)
        # 元素不存在则新增
        else:
            component_no = add_workspace_component(req.workspaceNo, component)
            # 存储元素的编号
            components.append(component_no)

    # 移除非请求中元素
    TWorkspaceComponent.deletes(
        TWorkspaceComponent.WORKSPACE_NO == req.workspaceNo,
        TWorkspaceComponent.COMPONENT_NO.notin_(components),
    )


def add_workspace_component(workspace_no: str, component: dict) -> str:
    # 新增元素
    component_no = new_id()
    TTestElement.insert(
        ELEMENT_NO=component_no,
        ELEMENT_NAME=component.get('elementName'),
        ELEMENT_DESC=component.get('elementDesc'),
        ELEMENT_TYPE=component.get('elementType'),
        ELEMENT_CLASS=component.get('elementClass'),
        ENABLED=component.get('enabled', ElementStatus.ENABLE.value)
    )
    # 创建元素属性
    add_element_property(component_no, component.get('property'))
    # 创建元素关联
    TWorkspaceComponent.insert(
        WORKSPACE_NO=workspace_no,
        COMPONENT_NO=component_no,
        COMPONENT_TYPE=component.get('elementType'),
        COMPONENT_SORT=component.get('elementIndex')
    )
    return component_no


@http_service
def query_workspace_settings(req):
    # 查询空间
    workspace = workspace_dao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='空间不存在')
    # 没有配置时返回空字典
    return workspace.COMPONENT_SETTINGS or {}


@http_service
def set_workspace_settings(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)
    # 查询空间
    workspace = workspace_dao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='空间不存在')
    # 更新组件设置
    workspace.update(COMPONENT_SETTINGS=req.settings)
