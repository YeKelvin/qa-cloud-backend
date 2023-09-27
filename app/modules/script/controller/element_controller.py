#!/usr/bin/ python3
# @File    : element_controller.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from app.modules.script.controller import blueprint
from app.modules.script.enum import PasteType
from app.modules.script.service import element_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/element/list')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_list():
    """分页查询元素列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('workspaceName'),
        Argument('elementNo'),
        Argument('elementName'),
        Argument('elementRemark'),
        Argument('elementType'),
        Argument('elementClass'),
        Argument('enabled'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_element_list(req)


@blueprint.get('/element/all')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_all():
    """查询全部元素"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('elementType'),
        Argument('elementClass'),
        Argument('enabled')
    ).parse()
    return service.query_element_all(req)


@blueprint.get('/element/all/with/children')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_all_with_children():
    """查询全部元素及其子代"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('elementType'),
        Argument('elementClass'),
        Argument('childType'),
        Argument('childClass'),
        Argument('enabled')
    ).parse()
    return service.query_element_all_with_children(req)


@blueprint.get('/element/info')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_info():
    """查询元素信息"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.query_element_info(req)


@blueprint.get('/element/children')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_children():
    """查询元素子代"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('depth', type=bool, required=True, default=True),
    ).parse()
    return service.query_element_children(req)


@blueprint.get('/elements/children')
@require_login
@require_permission('QUERY_ELEMENT')
def query_elements_children():
    """根据编号列表批量查询子代元素"""
    req = JsonParser(
        Argument('elements', type=list, required=True, nullable=False, help='元素编号列表不能为空'),
        Argument('depth', type=bool, required=True, default=True),
    ).parse()
    return service.query_elements_children(req)


@blueprint.post('/collection')
@require_login
@require_permission('CREATE_ELEMENT')
def create_collection():
    """新增集合元素"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementRemark'),
        Argument('elementType', required=True, nullable=False, help='元素类型不能为空'),
        Argument('elementClass', required=True, nullable=False, help='元素类不能为空'),
        Argument('property', required=True, nullable=False, help='元素属性不能为空'),
        Argument('attributes', type=dict),
        Argument('componentList', type=list)
    ).parse()
    return service.create_collection(req)


@blueprint.post('/element/child')
@require_login
@require_permission('CREATE_ELEMENT')
def create_element_child():
    """新增子代元素"""
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementRemark'),
        Argument('elementType', required=True, nullable=False, help='元素类型不能为空'),
        Argument('elementClass', required=True, nullable=False, help='元素类不能为空'),
        Argument('property', required=True, nullable=False, help='元素属性不能为空'),
        Argument('attributes', type=dict),
        Argument('componentList', type=list)
    ).parse()
    return service.create_element_child(req)


@blueprint.put('/element')
@require_login
@require_permission('MODIFY_ELEMENT')
def modify_element():
    """修改元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('elementName'),
        Argument('elementRemark'),
        Argument('property'),
        Argument('attributes', type=dict),
        Argument('componentList', type=list)
    ).parse()
    return service.modify_element(req)


@blueprint.delete('/element')
@require_login
@require_permission('REMOVE_ELEMENT')
def remove_element():
    """删除元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.remove_element(req)


@blueprint.put('/element/enable')
@require_login
@require_permission('MODIFY_ELEMENT')
def enable_element():
    """启用元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.enable_element(req)


@blueprint.put('/element/disable')
@require_login
@require_permission('MODIFY_ELEMENT')
def disable_element():
    """禁用元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.disable_element(req)


@blueprint.put('/element/state/toggle')
@require_login
@require_permission('MODIFY_ELEMENT')
def toggle_element_state():
    """切换元素状态"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.toggle_element_state(req)


@blueprint.post('/element/move')
@require_login
@require_permission('MOVE_ELEMENT')
def move_element():
    """移动元素"""
    req = JsonParser(
        Argument('sourceNo', required=True, nullable=False, help='Source元素编号不能为空'),
        Argument('targetIndex', type=int, required=True, nullable=False, help='Target元素序号不能为空'),
        Argument('targetRootNo', required=True, nullable=False, help='Target根元素编号不能为空'),
        Argument('targetParentNo', required=True, nullable=False, help='Target父元素编号不能为空')
    ).parse()
    return service.move_element(req)


@blueprint.post('/element/duplicate')
@require_login
@require_permission('COPY_ELEMENT')
def duplicate_element():
    """复制元素及其子代"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.duplicate_element(req)


@blueprint.post('/element/paste')
@require_login
@require_permission('PASTE_ELEMENT')
def paste_element():
    """剪贴元素"""
    req = JsonParser(
        Argument('sourceNo', required=True, nullable=False, help='Source元素编号不能为空'),
        Argument('targetNo', required=True, nullable=False, help='Target元素编号不能为空'),
        Argument('pasteType', required=True, nullable=False, enum=PasteType, help='剪贴类型不能为空')
    ).parse()
    return service.paste_element(req)


@blueprint.get('/element/components')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_components():
    """查询元素组件"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.query_element_components(req)


@blueprint.post('/element/collection/copy/to/workspace')
@require_login
@require_permission('COPY_ELEMENT')
def copy_collection_to_workspace():
    """复制集合到指定空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.copy_collection_to_workspace(req)


@blueprint.post('/element/collection/move/to/workspace')
@require_login
@require_permission('MOVE_ELEMENT')
def move_collection_to_workspace():
    """移动集合到指定空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.move_collection_to_workspace(req)


@blueprint.get('/element/workspace/components')
@require_login
@require_permission('QUERY_WORKSPACE_COMPONENT')
def query_workspace_components():
    """根据空间查询全部组件"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空')
    ).parse()
    return service.query_workspace_components(req)


@blueprint.post('/element/workspace/components')
@require_login
@require_permission('SET_WORKSPACE_COMPONENT')
def set_workspace_components():
    """设置空间组件"""
    """
    request:
    {
        "workspaceNo": "",
        "components": [
            {
                "elementNo": "",
                "elementName": "",
                "elementType": "",
                "elementClass": "",
                "elementIndex": "",
                "property": { ... },
                "matchRules": [ ... ]
            }
            ...
        ]
    }
    """
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('components', type=list)
    ).parse()
    return service.set_workspace_components(req)


@blueprint.get('/element/workspace/settings')
@require_login
@require_permission('QUERY_WORKSPACE_COMPONENT')
def query_workspace_settings():
    """查询空间组件设置"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空')
    ).parse()
    return service.query_workspace_settings(req)


@blueprint.post('/element/workspace/settings')
@require_login
@require_permission('SET_WORKSPACE_COMPONENT')
def set_workspace_settings():
    """设置空间组件设置"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('settings', type=dict)
    ).parse()
    return service.set_workspace_settings(req)
