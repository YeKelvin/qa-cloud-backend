#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_restricted_exemption_dao.py
# @Time    : 2022/4/22 15:51
# @Author  : Kelvin.Ye
from typing import List

from app.public.model import TWorkspaceRestrictedExemption


def select_first(**kwargs) -> TWorkspaceRestrictedExemption:
    return TWorkspaceRestrictedExemption.filter_by(**kwargs).first()


def select_by_restriction_and_exemption(restriction_no, exemption_no) -> TWorkspaceRestrictedExemption:
    return TWorkspaceRestrictedExemption.filter_by(RESTRICTION_NO=restriction_no, EXEMPTION_NO=exemption_no).first()


def select_all_by_restriction(restriction_no) -> List[TWorkspaceRestrictedExemption]:
    return TWorkspaceRestrictedExemption.filter_by(RESTRICTION_NO=restriction_no).all()


def select_all_by_restriction_and_type(restriction_no, exemption_type) -> List[TWorkspaceRestrictedExemption]:
    return TWorkspaceRestrictedExemption.filter_by(
        RESTRICTION_NO=restriction_no,
        EXEMPTION_TYPE=exemption_type
    ).all()


def delete_all_by_restriction(restriction_no):
    TWorkspaceRestrictedExemption.deletes_by(RESTRICTION_NO=restriction_no)


def delete_all_by_restriction_and_notin_exemption(restriction_no, exemption_type, *exemption_numbered_list):
    TWorkspaceRestrictedExemption.deletes(
        TWorkspaceRestrictedExemption.RESTRICTION_NO == restriction_no,
        TWorkspaceRestrictedExemption.EXEMPTION_TYPE == exemption_type,
        TWorkspaceRestrictedExemption.EXEMPTION_NO.notin_(*exemption_numbered_list)
    )
