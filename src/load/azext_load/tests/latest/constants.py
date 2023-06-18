# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

TEST_RESOURCES_DIR = os.path.join(os.path.dirname(__file__), r"resources")


class LoadConstants:

    # Test Plan constants
    LOAD_TEST_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, r"config.yaml")
    TEST_PLAN = os.path.join(TEST_RESOURCES_DIR, r"sample-JMX-file.jmx")
    ADDITIONAL_FILE = os.path.join(TEST_RESOURCES_DIR, r"additional-data.csv")
    FILE_NAME = "sample-JMX-file.jmx"

    ENV_VAR_DURATION_NAME = "duration_in_sec"
    ENV_VAR_DURATION_SHORT = "1"
    ENV_VAR_DURATION_LONG = "120"

    SECRETS = r"secret_name1=https://sample-kv.vault.azure.net/secrets/secret-name1/8022ff4b79f04a4ca6c3ca8e3820e757 secret_name2=https://sample-kv.vault.azure.net/secrets/secret-name2/8022ff4b79f04a4ca6c3ca8e3820e757"
    SECRET_NAME1 = "secret_name1"
    SECRET_NAME2 = "secret_name2"
    CERTIFICATE = r"cert=https://sample-kv.vault.azure.net/certificates/cert-name/0e35fd2807ce44368cf54274dd6f35cc"
    MULTIPLE_CERTIFICATE = r"cert1=https://sample-kv.vault.azure.net/certificates/cert-name1/0e35fd2807ce44368cf54274dd6f35cc cert2=https://sample-kv.vault.azure.net/certificates/cert-name2/0e35fd2807ce44368cf54274dd6f35cc"
    INVALID_SECRET = r"secret_name1=secret.url/secrets secret_name2=https://sample-kv.vault.azure.net/secrets/secret-name2/8022ff4b79f04a4ca6c3ca8e3820e757 secret_name3=https://sample-kv.vault.azure.net/secrets/secret-name3/8022ff4b79f04a4ca6c3ca8e3820e757"
    INVALID_ENV = "a"
    ENGINE_INSTANCE = 1

    INVALID_SUBNET_ID = r"/subscriptions/invalid/resource/id"
    KEYVAULT_REFERENCE_ID = r"/subscriptions/{subscription_id}/resourceGroups/sample-rg/providers/Microsoft.KeyVault/vaults/sample-kv"
    # App Component constants
    APP_COMPONENT_ID = r"/subscriptions/sapmle-subscription/resourceGroups/sample-rg/providers/Microsoft.Compute/virtualMachineScaleSets/sample-vmss"
    APP_COMPONENT_TYPE = r"Microsoft.Compute/virtualMachineScaleSets"
    APP_COMPONENT_NAME = r"temp-vmss"

    INVALID_APP_COMPONENT_ID = r"/subscriptions/invalid/resource/id"
    INVALID_APP_COMPONENT_TYPE = r"Microsoft.Storage/storageAccounts"

    # Server Metric constants
    SERVER_METRIC_ID = r"{}/providers/microsoft.insights/metricdefinitions/Availability"
    SERVER_METRIC_ID2 = r"/subscriptions/0a00b000-0aa0-0aa0-aaa0-000000000/resourceGroups/sample-rg/providers/Microsoft.Storage/storageAccounts/sample-storage-account"
    SERVER_METRIC_NAME = r"Availability"
    SERVER_METRIC_NAMESPACE = r"microsoft.storage/storageaccounts"
    AGGREGATION = "Average"

    INVALID_SERVER_METRIC_ID = r"/subscriptions/invalid/resource/id"



class LoadTestConstants(LoadConstants):
    # Test IDs for load test commands
    VALID_TEST_ID = "valid-test-case_testid"
    INVALID_TEST_ID = "invalid-test-case-testid"
    INVALID_UPDATE_TEST_ID = "invalid-update-test-case"
    DESCRIPTION = r"Sample_test_description"
    DISPLAY_NAME = r"Sample_test_display_name"


class LoadTestRunConstants(LoadConstants):
    # Metric constants
    METRIC_NAME = "VirtualUsers"
    METRIC_NAMESPACE = "LoadTestRunMetrics"
    METRIC_DIMENSION_NAME = "RequestName"
    METRIC_DIMENSION_VALUE = "HTTP Request"
    METRIC_FILTERS_ALL = "*"
    METRIC_FILTERS_VALUE_ALL = f"{METRIC_DIMENSION_NAME}=*"
    METRIC_FILTERS_VALUE_SPECIFIC = f"{METRIC_DIMENSION_NAME}={METRIC_DIMENSION_VALUE}"
    AGGREGATION = "Average"

    DESCRIPTION = r"Sample_testrun_description"
    DISPLAY_NAME = r"Sample_testrun_display_name"

    VALID_TEST_ID = "valid-testrun-case-testid"
    VALID_TEST_RUN_ID = "valid-testrun-case-testrunid"
    VALID_TEST_RUN_ID_LONG = "valid-testrun-case-long-testrunid"
    VALID_TEST_RUN_ID_LONG2 = "valid-testrun-case-long-testrunid2"
    INVALID_TEST_RUN_ID = r"A$%invalid-testrun-case-testrunid"
    