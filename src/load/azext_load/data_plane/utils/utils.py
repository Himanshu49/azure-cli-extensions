# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import uuid
from enum import EnumMeta

import requests
import yaml
from azext_load.data_plane.utils import validators
from azext_load.vendored_sdks.loadtesting_mgmt import LoadTestMgmtClient
from azure.cli.core.azclierror import FileOperationError, InvalidArgumentValueError
from knack.log import get_logger
from msrestazure.tools import is_valid_resource_id, parse_resource_id

from .models import IdentityType, AllowedFileTypes

logger = get_logger(__name__)


def get_load_test_resource_endpoint(
    cred, load_test_resource, resource_group=None, subscription_id=None
):
    if subscription_id is None:
        return None
    if is_valid_resource_id(load_test_resource):
        # load_test_resource is a resource id
        logger.debug(
            "load-test-resource '%s' is an Azure Resource Id", load_test_resource
        )
        parsed = parse_resource_id(load_test_resource)
        resource_group, name = parsed["resource_group"], parsed["name"]
        if subscription_id != parsed["subscription"]:
            logger.info(
                "Subscription ID in load-test-resource parameter and CLI context do not match - %s and %s",
                subscription_id,
                parsed["subscription"],
            )
            return None
    else:
        # load_test_resource is a name
        logger.debug(
            "load-test-resource '%s' is an Azure Load Testing resource name. Using resource group name %s",
            load_test_resource,
            resource_group,
        )
        if resource_group is None:
            raise InvalidArgumentValueError(
                "Resource group name must be specified when load-test-resource is a name"
            )
        name = load_test_resource

    mgmt_client = LoadTestMgmtClient(credential=cred, subscription_id=subscription_id)
    data_plane_uri = mgmt_client.load_tests.get(resource_group, name).data_plane_uri
    logger.info("Azure Load Testing data plane URI: %s", data_plane_uri)
    return data_plane_uri


def get_login_credentials(cli_ctx, subscription_id=None):
    from azure.cli.core._profile import Profile

    credential = Profile(cli_ctx=cli_ctx).get_login_credentials(
        subscription_id=subscription_id
    )
    logger.debug("Fetched login credentials for subscription %s", subscription_id)
    return credential


def get_admin_data_plane_client(cmd, load_test_resource, resource_group_name=None):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    return admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )


def get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name=None):
    from azext_load.data_plane.client_factory import testrun_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    return testrun_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )


def get_enum_values(enum):
    if not isinstance(enum, EnumMeta):
        raise InvalidArgumentValueError(f"Invalid enum type: {type(enum)}")
    return [item.value for item in enum]


def download_file(url, file_path):
    logger.debug("Downloading file started")
    response = None
    retries = 3
    ex = None
    while retries > 0:
        try:
            response = requests.get(url, stream=True, allow_redirects=True)
            break
        except Exception as e:
            ex = e
            retries -= 1
            logger.debug(
                "Exception occurred while downloading file: %s. Retrying the request. Retries remaining: %d",
                str(ex),
                retries,
            )
    if retries == 0:
        msg = "Request for {} failed after all retries: {}".format(url, str(ex))
        logger.debug(msg)
        raise Exception(msg)

    if response:
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # ignore keep-alive new chunks
                    f.write(chunk)
    logger.debug("Downloading file completed")


def upload_file_to_test(client, test_id, file_path, file_type=None, wait=False):
    logger.debug(
        "Uploading file %s for the test %s with 'wait' %s",
        file_path,
        test_id,
        "enabled" if wait else "disabled",
    )
    file_path = validators._validate_path(file_path, is_dir=False)
    with open(file_path, "rb") as file:
        upload_poller = client.begin_upload_test_file(
            test_id,
            file_name=os.path.basename(file.name),
            file_type=file_type,
            body=file,
        )
        response = (
            upload_poller.result()
            if wait
            else upload_poller.polling_method().resource()
        )
        logger.debug(
            "Upload result for file with --wait%s passed: %s",
            "" if wait else " not",
            response,
        )
        return response


def parse_cert(certificate):
    logger.debug("Parsing certificate")
    if len(certificate) != 1:
        raise ValueError("Only one certificate is supported")
    certificate = certificate[0]
    name, value = certificate.get("name"), certificate.get("value")
    if not validators._validate_akv_url(value, "certificates"):
        raise ValueError(f"Invalid AKV Certificate URL: {value}")
    certificate = {
        "name": name,
        "type": "AKV_CERT_URI",
        "value": value,
    }
    logger.debug("Parsed certificate: %s", certificate)
    logger.debug("Certificate parsed successfully")
    return certificate


def parse_secrets(secrets):
    logger.debug("Parsing secrets")
    secrets_dict = {}
    for secret in secrets:
        name, value = secret.get("name"), secret.get("value")
        if name is None or value is None:
            raise ValueError("Both name and value are required for secret")
        if not validators._validate_akv_url(value, "secrets"):
            raise ValueError(f"Invalid AKV Certificate URL: {value}")
        secrets_dict[name] = {
            name: {
                "type": "AKV_SECRET_URI",
                "value": value,
            }
        }
    logger.debug("Parsed secrets: %s", secrets_dict)
    logger.debug("Secrets parsed successfully")
    return secrets_dict


def parse_env(envs):
    logger.debug("Parsing environment variables")
    env_dict = {}
    for env in envs:
        name, value = env.get("name"), env.get("value")
        if name is None:
            raise ValueError("Name is required for environment variable")
        if value is None:
            value = ""
        env_dict[name] = value
    logger.debug("Parsed environment variables: %s", env_dict)
    logger.debug("Environment variables parsed successfully")
    return env_dict


def load_yaml(file_path):
    logger.debug("Loading yaml file: %s", file_path)
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            logger.info("Yaml file loaded successfully")
            return data
    except yaml.YAMLError as e:
        raise ValueError(f"Error loading yaml file: {e}")
    except Exception as e:
        logger.debug(
            "Exception occurred while parsing load test configuration file: %s",
            str(e),
        )
        raise FileOperationError(
            "Invalid load test configuration file : %s. Please check the file path and format. Exception: %s",
            file_path,
            str(e),
        )


def convert_yaml_to_test(data):
    new_body = {}
    if "displayName" in data:
        new_body["displayName"] = data["displayName"]
    if "description" in data:
        new_body["description"] = data["description"]
    new_body["keyvaultReferenceIdentityType"] = IdentityType.SystemAssigned
    if "keyvaultReferenceIdentityId" in data:
        new_body["keyvaultReferenceIdentityId"] = data["keyvaultReferenceIdentityId"]
        new_body["keyvaultReferenceIdentityType"] = IdentityType.UserAssigned

    if "subnetId" in data:
        new_body["subnetId"] = data["subnetId"]

    new_body["loadTestConfiguration"] = {}
    new_body["loadTestConfiguration"]["engineInstances"] = data.get(
        "engineInstances", 1
    )
    if data.get("certificate"):
        new_body["certificate"] = parse_cert(data.get("certificate"))
    if data.get("secrets"):
        new_body["secrets"] = parse_secrets(data.get("secrets"))
    if data.get("env"):
        new_body["environmentVariables"] = parse_env(data.get("env"))

    # quick test and split csv not supported currently in CLI
    new_body["loadTestConfiguration"]["quickStartTest"] = False
    if data.get("quickStartTest"):
        logger.warning(
            "Quick start test is not supported currently in CLI. Please use portal to run quick start test"
        )
    if data.get("splitAllCSVs"):
        new_body["loadTestConfiguration"]["splitAllCSVs"] = data.get("splitAllCSVs")

    if data.get("failureCriteria"):
        new_body["passFailCriteria"] = {}
        new_body["passFailCriteria"]["passFailMetrics"] = {}
        for index, items in enumerate(data["failureCriteria"]):
            id = get_random_uuid()
            name = list(items.keys())[0]
            components = list(items.values())[0]
            new_body["passFailCriteria"]["passFailMetrics"][id] = {}
            new_body["passFailCriteria"]["passFailMetrics"][id][
                "aggregate"
            ] = components.split("(")[0].strip()
            new_body["passFailCriteria"]["passFailMetrics"][id]["clientMetric"] = (
                components.split("(")[1].split(")")[0].strip()
            )
            new_body["passFailCriteria"]["passFailMetrics"][id][
                "condition"
            ] = components.split(")")[1].strip()[0]
            new_body["passFailCriteria"]["passFailMetrics"][id][
                "value"
            ] = components.split(
                new_body["passFailCriteria"]["passFailMetrics"][id]["condition"]
            )[
                1
            ].strip()
            new_body["passFailCriteria"]["passFailMetrics"][id]["requestName"] = name
    return new_body


def create_or_update_body(
    test_id,
    body,
    yaml_test_body=None,
    display_name=None,
    test_description=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    key_vault_reference_identity=None,
    subnet_id=None,
    split_csv=None,
):
    logger.info("Creating a request body for create or update test")
    new_body = {}
    if display_name is not None:
        new_body["displayName"] = display_name
    else:
        new_body["displayName"] = body.get("displayName", test_id)

    if test_description is not None:
        new_body["description"] = test_description
    else:
        new_body["description"] = body.get("description")

    new_body["keyvaultReferenceIdentityType"] = IdentityType.SystemAssigned
    if key_vault_reference_identity is not None:
        new_body["keyvaultReferenceIdentityId"] = key_vault_reference_identity
        new_body["keyvaultReferenceIdentityType"] = IdentityType.UserAssigned
    elif body.get("keyvaultReferenceIdentityId") is not None:
        new_body["keyvaultReferenceIdentityId"] = body.get(
            "keyvaultReferenceIdentityId"
        )
        new_body["keyvaultReferenceIdentityType"] = body.get(
            "keyvaultReferenceIdentityType", IdentityType.UserAssigned
        )

    if subnet_id is not None:
        new_body["subnetId"] = subnet_id
    elif body.get("subnetId"):
        new_body["subnetId"] = body.get("subnetId")

    if env is not None:
        new_body["environmentVariables"] = body.get("environmentVariables", {})
        new_body["environmentVariables"].update(env)

    if secrets is not None:
        new_body["secrets"] = body.get("secrets", {})
        new_body["secrets"].update(secrets)

    if certificate is not None:
        new_body["certificate"] = certificate
    elif body.get("certificate"):
        new_body["certificate"] = body.get("certificate")

    new_body["loadTestConfiguration"] = body.get("loadTestConfiguration", {})
    if engine_instances:
        new_body["loadTestConfiguration"]["engineInstances"] = engine_instances
    else:
        new_body["loadTestConfiguration"]["engineInstances"] = body.get(
            "loadTestConfiguration", {}
        ).get("engineInstances", 1)
    # quick test and split csv not supported currently
    new_body["loadTestConfiguration"]["quickStartTest"] = False
    new_body["loadTestConfiguration"]["splitAllCSVs"] = True if split_csv else False
    logger.debug("Request body for create or update test: %s", new_body)
    return new_body


def create_or_update_test_run_body(
    test_id,
    display_name=None,
    description=None,
    env=None,
    secrets=None,
    certificate=None,
):
    logger.info("Creating a request body for create test run")
    new_body = {"testId": test_id}
    if display_name is not None:
        new_body["displayName"] = display_name
    if description is not None:
        new_body["description"] = description
    if env is not None:
        new_body["environmentVariables"] = env
    if secrets is not None:
        new_body["secrets"] = secrets
    if certificate is not None:
        new_body["certificate"] = certificate
    logger.debug("Request body for create test run: %s", new_body)
    return new_body


def upload_files_helper(client, test_id, yaml, test_plan, load_test_config_file, wait):
    files = client.list_test_files(test_id)
    if yaml:
        user_prop_file = yaml.get("properties", {}).get("userPropertyFile")
        if user_prop_file is not None:
            logger.info("Uploading user property file %s", user_prop_file)
            file_name = os.path.basename(user_prop_file)
            for file in files:
                if AllowedFileTypes.USER_PROPERTIES.value == file["fileType"]:
                    client.delete_test_file(test_id, file["fileName"])
                    logger.info(
                        "File of type '%s' already exists in test %s. Deleting it!",
                        AllowedFileTypes.USER_PROPERTIES,
                        test_id,
                    )
                    break
            file_response = upload_file_to_test(
                client,
                test_id,
                user_prop_file,
                file_type=AllowedFileTypes.USER_PROPERTIES,
                wait=wait,
            )
            logger.info(
                "Uploaded file '%s' of type %s to test %s",
                file_name,
                AllowedFileTypes.USER_PROPERTIES,
                test_id,
            )

    if yaml and yaml.get("configurationFiles") is not None:
        logger.info("Uploading additional artifacts")
        for config_file in yaml.get("configurationFiles"):
            file_name = os.path.basename(config_file)
            if file_name in [file["fileName"] for file in files]:
                client.delete_test_file(test_id, file_name)
                logger.info(
                    "File with name '%s' already exists in test %s. Deleting it!",
                    file_name,
                    test_id,
                )
            upload_file_to_test(
                client,
                test_id,
                config_file,
                file_type=AllowedFileTypes.ADDITIONAL_ARTIFACTS,
                wait=wait,
            )
            logger.info(
                "Uploaded file '%s' of type %s to test %s",
                file_name,
                AllowedFileTypes.ADDITIONAL_ARTIFACTS,
                test_id,
            )

    if test_plan is None and yaml is not None and yaml.get("testPlan"):
        test_plan = yaml.get("testPlan")
        if not os.path.isabs(test_plan) and load_test_config_file:
            yaml_dir = os.path.dirname(load_test_config_file)
            test_plan = os.path.join(yaml_dir, test_plan)
    if test_plan:
        logger.info("Uploading test plan file %s", test_plan)
        file_name = os.path.basename(test_plan)
        for file in files:
            if validators.AllowedFileTypes.JMX_FILE.value == file["fileType"]:
                client.delete_test_file(test_id, file["fileName"])
                logger.info(
                    "File with name '%s' already exists in test %s. Deleting it!",
                    file_name,
                    test_id,
                )
                break
        file_response = upload_file_to_test(
            client,
            test_id,
            test_plan,
            file_type=validators.AllowedFileTypes.JMX_FILE,
            wait=wait,
        )
        if wait and file_response.get("validationStatus") != "VALIDATION_SUCCESS":
            raise FileOperationError(
                f"Test plan file {test_plan} is not valid. Please check the file and try again."
            )


def get_random_uuid():
    return str(uuid.uuid4())