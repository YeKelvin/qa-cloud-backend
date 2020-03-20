#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : number_generator
# @Time    : 2020/3/20 14:03
# @Author  : Kelvin.Ye
from server.librarys.sequence import Sequence

__seq_element_no__ = Sequence('seq_element_no')
__seq_property_no__ = Sequence('seq_property_no')


def generate_element_no():
    return 'EL' + str(__seq_element_no__.next_value()).zfill(10)


def generate_property_no():
    return 'PROP' + str(__seq_property_no__.next_value()).zfill(10)
