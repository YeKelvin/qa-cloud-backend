#!/usr/bin/ python3
# @File    : element_controller.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from app.script.controller import blueprint
from app.script.enum import PasteType
from app.script.service import element_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.parser import ListParser


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


@blueprint.get('/element/all/in/private')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_all_in_private():
    """查询用户空间下的所有元素（用于私人空间）"""
    req = JsonParser(
        Argument('elementType'),
        Argument('elementClass'),
        Argument('enabled')
    ).parse()
    return service.query_element_all_in_private(req)


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
        Argument('elementNos', type=list, required=True, nullable=False, help='元素编号列表不能为空'),
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
        Argument('options', type=dict),
        Argument('builtins', type=list)
    ).parse()
    return service.create_collection(req)


@blueprint.post('/element/child')
@require_login
@require_permission('CREATE_ELEMENT')
def create_element_child():
    """
    新增子代元素
    request:
    {
        "rootNo": "",
        "parentNo": "",
        "child": {
            "elementName": "",
            "elementRemark": "",
            "elementType": "",
            "elementClass": "",
            "property": { ... },
            "options": { ... },
            "builtins": [ ... ]
        }
    }
    """
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('child', type=dict, required=True, nullable=False, help='子元素不能为空')
    ).parse()
    return service.create_element_child(req)


@blueprint.post('/element/children')
@require_login
@require_permission('CREATE_ELEMENT')
def create_element_children():
    """
    根据列表新增子代元素
    request:
    {
        "rootNo": "",
        "parentNo": "",
        "children": [
            {
                "elementName": "",
                "elementRemark": "",
                "elementType": "",
                "elementClass": "",
                "property": { ... },
                "options": { ... },
                "builtins": [ ... ]
            }
            ...
        ]
    }
    """
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('children', type=list, required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.create_element_children(req)


@blueprint.put('/element')
@require_login
@require_permission('MODIFY_ELEMENT')
def modify_element():
    """修改元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('elementName'),
        Argument('elementRemark'),
        Argument('enabled'),
        Argument('property'),
        Argument('options', type=dict),
        Argument('builtins', type=list),
    ).parse()
    return service.modify_element(req)


@blueprint.delete('/element')
@require_login
@require_permission('REMOVE_ELEMENT')
def remove_element():
    """删除元素"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.remove_element(req)


@blueprint.patch('/element/enable')
@require_login
@require_permission('MODIFY_ELEMENT')
def enable_element():
    """启用元素"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.enable_element(req)


@blueprint.patch('/element/disable')
@require_login
@require_permission('MODIFY_ELEMENT')
def disable_element():
    """禁用元素"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.disable_element(req)


@blueprint.patch('/element/state/toggle')
@require_login
@require_permission('MODIFY_ELEMENT')
def toggle_element_state():
    """切换元素状态"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.toggle_element_state(req)


@blueprint.post('/element/move')
@require_login
@require_permission('MOVE_ELEMENT')
def move_element():
    """移动元素"""
    req = JsonParser(
        Argument('sourceNo', required=True, nullable=False, help='source元素编号不能为空'),
        Argument('targetRootNo', required=True, nullable=False, help='target根元素编号不能为空'),
        Argument('targetParentNo', required=True, nullable=False, help='target父元素编号不能为空'),
        Argument('targetSortNo', type=int, required=True, nullable=False, help='target元素序号不能为空')
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
        Argument('sourceNo', required=True, nullable=False, help='source元素编号不能为空'),
        Argument('targetNo', required=True, nullable=False, help='target元素编号不能为空'),
        Argument('pasteType', required=True, nullable=False, enum=PasteType, help='剪贴类型不能为空')
    ).parse()
    return service.paste_element(req)


@blueprint.get('/element/httpheader/template/refs')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_httpheader_template_refs():
    """查询HTTP请求头引用"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.query_element_httpheader_template_refs(req)


@blueprint.post('/element/httpheader/template/refs')
@require_login
@require_permission('CREATE_ELEMENT')
def create_element_httpheader_template_refs():
    """新增HTTP请求头引用"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('templateNos', type=list, required=True, nullable=False, help='模板编号列表不能为空')
    ).parse()
    return service.create_element_httpheader_template_refs(req)


@blueprint.put('/element/httpheader/template/refs')
@require_login
@require_permission('MODIFY_ELEMENT')
def modify_element_httpheader_template_refs():
    """修改HTTP请求头引用"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('templateNos', type=list, required=True, nullable=False, help='模板编号列表不能为空')
    ).parse()
    return service.modify_element_httpheader_template_refs(req)


@blueprint.get('/element/builtins')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_builtins():
    """查询内置元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.query_element_builtins(req)


@blueprint.post('/element/builtins')
@require_login
@require_permission('CREATE_ELEMENT')
def create_element_builtins():
    """新增内置元素"""
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('children', type=list, required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.create_element_builtins(req)


@blueprint.put('/element/builtins')
@require_login
@require_permission('MODIFY_ELEMENT')
def modify_element_builtins():
    """修改内置元素"""
    req = ListParser().parse()
    return service.modify_element_builtins(req)


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


@blueprint.post('/element/http/sampler')
@require_login
@require_permission('CREATE_ELEMENT')
def create_http_sampler():
    """
    新增HTTP取样器
    request:
    {
        "rootNo": "",
        "parentNo": "",
        "child": {
            "elementName": "",
            "elementRemark": "",
            "property": { ... },
            "builtins": [
                    "elementNo": "",
                    "elementName": "",
                    "elementType": "",
                    "elementClass": "",
                    "property": { ... },
                    "sortNumber": ""
                }
                ...
            ],
            "headerTemplateNos": [ ... ]
        }
    }
    """
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('child', type=dict, required=True, nullable=False, help='元素信息不能为空')
    ).parse()
    return service.create_http_sampler(req)


@blueprint.put('/element/http/sampler')
@require_login
@require_permission('MODIFY_ELEMENT')
def modify_http_sampler():
    """
    修改HTTP取样器
    request:
    {
        "elementNo": "",
        "elementName": "",
        "elementRemark": "",
        "property": { ... },
        "builtins": [
            {
                "elementNo": "",
                "elementName": "",
                "elementType": "",
                "elementClass": "",
                "property": { ... },
                "sortNumber": ""
            }
            ...
         ],
        "headerTemplateNos": [ ... ]
    }
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementRemark'),
        Argument('property', required=True, nullable=False, help='元素属性不能为空'),
        Argument('builtins', type=list),
        Argument('headerTemplateNos', type=list)
    ).parse()
    return service.modify_http_sampler(req)


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
    """
    设置空间组件
    request:
    {
        "workspaceNo": "",
        "components": [

            {
                "elementNo": "",
                "elementName": "",
                "elementType": "",
                "elementClass": "",
                "property": { ... },
                "matchRules": [ ... ],
                "sortNumber": ""
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
