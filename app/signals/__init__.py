#!/usr/bin python3
# @Module  : signals
# @File    : __init__.py
# @Time    : 2023-04-21 14:38:01
# @Author  : Kelvin.Ye
from blinker import signal


# element
element_moved_signal = signal('RecordMoveElement')
element_copied_signal = signal('RecordCopeElement')
element_sorted_signal = signal('RecordOrderElement')
element_created_signal = signal('RecordCreateElement')
element_removed_signal = signal('RecordRemoveElement')
element_modified_signal = signal('RecordModifyElement')
element_transferred_signal = signal('RecordTransferElement')

# api log
restapi_log_signal = signal('RestAPILog')
openapi_log_signal = signal('OpenAPILog')

# system
record_insert_signal = signal('RecordInsert')
record_update_signal = signal('RecordUpdate')
record_delete_signal = signal('RecordDelete')


from . import element_reveiver  # noqa
from . import openapi_receiver  # noqa
from . import system_receiver   # noqa
