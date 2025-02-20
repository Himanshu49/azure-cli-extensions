# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-locals

import os


from azext_load.data_plane.utils.models import (
    AllowedTriggerStates,
    RecurrenceTypes,
)
from azure.cli.core.azclierror import InvalidArgumentValueError, FileOperationError
from azure.core.exceptions import ResourceNotFoundError
from knack.log import get_logger

logger = get_logger(__name__)

def create_trigger_schedule(
    cmd,
    load_test_resource,
    resource_group_name,
    trigger_id,
    description,
    display_name,
    start_date_time,
    recurrence_type,
    recurrence_properties,
    end_after_occurrence,
    end_after_date_time,
    test_ids,
):
    logger.info(
        "Creating trigger schedule with name"
    )
    # client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    # response = client.create_trigger_schedule(
    #     test_id, schedule_name, schedule, enabled, tags
    # )
    # logger.debug("Created trigger schedule: %s", response)
    # logger.info("Creating trigger schedule completed")
    # return response

def update_trigger_schedule(
    cmd,
    load_test_resource,
    resource_group_name,
    trigger_id,
    description,
    display_name,
    start_date_time,
    recurrence_type,
    recurrence_properties,
    end_after_occurrence,
    end_after_date_time,
    test_ids,
    state,
):
    logger.info(
        "Updating trigger schedule with name"
    )
    # client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    # response = client.update_trigger_schedule(
    #     test_id, schedule_name, schedule, enabled, tags
    # )
    # logger.debug("Updated trigger schedule: %s", response)
    # logger.info("Updating trigger schedule completed")
    # return response

def delete_trigger_schedule(
    cmd,
    load_test_resource,
    resource_group_name,
    trigger_id,
):
    logger.info(
        "Deleting trigger schedule with name"
    )
    # client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    # response = client.delete_trigger_schedule(test_id, schedule_name)
    # logger.debug("Deleted trigger schedule: %s", response)
    # logger.info("Deleting trigger schedule completed")
    # return response

def list_trigger_schedules(
    cmd,
    load_test_resource,
    resource_group_name,
    test_ids,
    state,
):
    logger.info("Listing trigger schedules")
    # client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    # response = client.list_trigger_schedules()
    # logger.debug("Listed trigger schedules: %s", response)
    # logger.info("Listing trigger schedules completed")
    # return response

def get_trigger_schedule(
    cmd,
    load_test_resource,
    resource_group_name,
    trigger_id,
):
    logger.info(
        "Getting trigger schedule with name"
    )
    # client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    # response = client.get_trigger_schedule(test_id, schedule_name)
    # logger.debug("Got trigger schedule: %s", response)
    # logger.info("Getting trigger schedule completed")
    # return response

def pause_trigger_schedule(
    cmd,
    load_test_resource,
    resource_group_name,
    trigger_id,
):
    logger.info(
        "Pausing trigger schedule with name"
    )
    # client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    # response = client.pause_trigger_schedule(test_id, schedule_name)
    # logger.debug("Paused trigger schedule: %s", response)
    # logger.info("Pausing trigger schedule completed")
    # return response

def enable_trigger_schedule(
    cmd,
    load_test_resource,
    resource_group_name,
    trigger_id,
):
    logger.info(
        "Enabling trigger schedule with name"
    )
    # client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    # response = client.enable_trigger_schedule(test_id, schedule_name)
    # logger.debug("Enabled trigger schedule: %s", response)
    # logger.info("Enabling trigger schedule completed")
    # return response
