# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=line-too-long

from azext_load.data_plane.utils import argtypes


def load_arguments(self, _):
    # Load Trigger Schedule
    with self.argument_context("load trigger schedule") as c:
        c.argument("load_test_resource", argtypes.load_test_resource)
        c.argument("resource_group_name", argtypes.resource_group)
        c.argument("trigger_id", argtypes.trigger_id)

    # Load Trigger Schedule Create
    with self.argument_context("load trigger schedule create") as c:
        c.argument("description", argtypes.trigger_description)
        c.argument("display_name", argtypes.trigger_display_name)
        c.argument("start_date_time", argtypes.start_date_time)
        c.argument("recurrence_type", argtypes.recurrence_type)
        c.argument("recurrence_properties", argtypes.recurrence_properties)
        c.argument("end_after_occurrence", argtypes.end_after_occurrence)
        c.argument("end_after_date_time", argtypes.end_after_date_time)
        c.argument("test_ids", argtypes.test_ids)
    
    # Load Trigger Schedule Update
    with self.argument_context("load trigger schedule update") as c:
        c.argument("description", argtypes.trigger_description)
        c.argument("display_name", argtypes.trigger_display_name)
        c.argument("start_date_time", argtypes.start_date_time)
        c.argument("recurrence_type", argtypes.recurrence_type)
        c.argument("recurrence_properties", argtypes.recurrence_properties)
        c.argument("end_after_occurrence", argtypes.end_after_occurrence)
        c.argument("end_after_date_time", argtypes.end_after_date_time)
        c.argument("test_ids", argtypes.test_ids)
        c.argument("state", argtypes.state)

    # Load Trigger Schedule List
    with self.argument_context("load trigger schedule list") as c:
        c.argument("trigger_id", argtypes.trigger_id)
        c.argument("state", argtypes.state)
        c.argument("test_ids", argtypes.test_ids)
    