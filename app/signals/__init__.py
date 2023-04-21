#!/usr/bin python3
# @Module  : signals
# @File    : __init__.py
# @Time    : 2023-04-21 14:38:01
# @Author  : Kelvin.Ye
from blinker import signal


restapi_log_signal = signal('RestAPILog')
openapi_log_signal = signal('OpenAPILog')
record_insert_signal = signal('RecordInsert')
record_update_signal = signal('RecordUpdate')
record_delete_signal = signal('RecordDelete')


from . import openapi_subscriber    # noqa
from . import system_subscriber     # noqa
