#!/usr/bin python3
# @File    : typing.py
# @Time    : 2023-10-08 17:32:38
# @Author  : Kelvin.Ye
from typing import TypedDict


class TypedElement(TypedDict):
    workspaceNo: str
    enabled: bool
    elementNo: str
    elementName: str
    elementDesc: str
    elementType: str
    elementClass: str
    elementIndex: str
    elementAttrs: dict
    elementProps: dict
    elementCompos: dict
