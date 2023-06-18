# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import tempfile

from azext_load.tests.latest.constants import LoadTestConstants
from azext_load.tests.latest.helper import create_test, delete_test
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    VirtualNetworkPreparer,
    StorageAccountPreparer,
    ScenarioTest,
    create_random_name,
)

rg_params = {
    "name_prefix": "clitest-load-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-load-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}
vnet_params = {
    "name_prefix": "clitest-load-",
    "location": "eastus",
    "key": "virtual_network",
    "parameter_name": "vnet",
    "resource_group_key": "resource_group",
    "resource_group_parameter_name": "rg",
    "random_name_length": 30,
}
sa_params = {
    "name_prefix": "clitestload",
    "location": "eastus",
    "key": "storage_account",
    "parameter_name": "storage_account",
    "resource_group_parameter_name": "rg",
    "length": 20,
}

class LoadTestScenario(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenario, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})

    @ResourceGroupPreparer(**rg_params)
    @VirtualNetworkPreparer(**vnet_params)
    @LoadTestResourcePreparer(**load_params)
    @StorageAccountPreparer(**sa_params)
    def test_load_test_valid(self, rg, load, vnet):
        #GET STORAGE ACCOUNT ID
        result= self.cmd("az storage account show --name {storage_account} --resource-group {resource_group}").get_output_in_json()
        storage_account_id = result["id"]
        storage_account_name = result["name"]
        storage_account_type = result["type"]
        storage_account_kind = result["kind"]
        #GET SUBNET ID
        result= self.cmd("az network vnet subnet list --resource-group {resource_group} --vnet-name {virtual_network}").get_output_in_json()
        subnet_id = result[0]["id"]

        #keyvault_id = self.cmd("az keyvault show --name {key_vault} --resource-group {resource_group}").get_output_in_json()["id"]
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.VALID_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "certificate": LoadTestConstants.CERTIFICATE,
                "secret": LoadTestConstants.SECRETS,
                "description": LoadTestConstants.DESCRIPTION,
                "display_name": LoadTestConstants.DISPLAY_NAME,
                "engine_instance": LoadTestConstants.ENGINE_INSTANCE,
                "keyvault_reference_id": LoadTestConstants.KEYVAULT_REFERENCE_ID,
                "split_csv": "yes",
                "subnet_id": subnet_id
            }
        )
        
        checks=[JMESPathCheck("testId", self.kwargs["test_id"]),
                JMESPathCheck("loadTestConfiguration.engineInstances", self.kwargs["engine_instance"]),
                JMESPathCheck("description", self.kwargs["description"]),
                JMESPathCheck("displayName", self.kwargs["display_name"]),
                JMESPathCheck("keyvaultReferenceIdentityId", self.kwargs["keyvault_reference_id"]),
                JMESPathCheck("subnetId", self.kwargs["subnet_id"]),
                JMESPathCheck("loadTestConfiguration.splitAllCSVs", True),
                JMESPathCheck("environmentVariables.rps", '10')]
        #Create load test with all parameters
        response = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" '
            "--env rps=10 "
            "--description {description} "
            "--display-name {display_name} "
            "--engine-instance {engine_instance} "
            "--certificate {certificate} "
            "--secret {secret} "
            "--keyvault-reference-id {keyvault_reference_id} "
            "--subnet-id {subnet_id} "
            "--split-csv {split_csv} ",
            checks=checks,
        ).get_output_in_json()

        assert self.kwargs["certificate"] == response.get("certificate").get("name") + "=" +response.get("certificate").get("value")
        assert self.kwargs["secret"] == LoadTestConstants.SECRET_NAME1+"="+response.get("secrets").get(LoadTestConstants.SECRET_NAME1).get("value") + " " + LoadTestConstants.SECRET_NAME2+"="+response.get("secrets").get(LoadTestConstants.SECRET_NAME2).get("value")

        #2 UPDATE THIS TO REM SPLIT CSV
        self.kwargs.update(
            {
                "engine_instance": 11,
                "keyvault_reference_id": "null",
                "split_csv": "NO"
            }
        )
        checks=[JMESPathCheck("loadTestConfiguration.engineInstances", self.kwargs["engine_instance"]),
                JMESPathCheck("keyvaultReferenceIdentityType", "SystemAssigned"),
                JMESPathCheck("loadTestConfiguration.splitAllCSVs", False)]
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--engine-instance {engine_instance} "
            "--keyvault-reference-id {keyvault_reference_id} "
            "--split-csv {split_csv} ",
            checks=checks,
        ).get_output_in_json()
        
        #3 SHOW TEST TO CHECK IF KEYVAULTREFERENCEIDENTITYTYPE AND SPLIT CSV IS REMOVED
        response = self.cmd(
            "az load test show "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
        ).get_output_in_json()

        assert self.kwargs["test_id"] == response.get("testId")
        assert not response.get("loadTestConfiguration").get("splitAllCSVs")
        assert "SystemAssigned" == response.get("keyvaultReferenceIdentityType")

        #4 DOWNLOAD ALL FILES
        with tempfile.TemporaryDirectory(
            prefix="clitest-load-", suffix=create_random_name(prefix="", length=5)
        ) as temp_dir:
            self.kwargs.update({"path": temp_dir})

            self.cmd(
                "az load test download-files "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--path "{path}"'
            )

            files = self.cmd(
                "az load test file list "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} ",
            ).get_output_in_json()

            files_in_dir = [
                f
                for f in os.listdir(temp_dir)
                if os.path.isfile(os.path.join(temp_dir, f))
            ]
            for file in files:
                assert file["fileName"] in files_in_dir
        
        #5 DELETE A FILE
        self.kwargs.update(
            {
                "path": temp_dir,
                "file_name": LoadTestConstants.FILE_NAME,
                "test_plan": LoadTestConstants.TEST_PLAN,
            }
        )       
        self.cmd(
            "az load test file delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--file-name {file_name} "
            "--yes"
        )

        files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert self.kwargs["file_name"] not in [file["fileName"] for file in files]

        #6 UPLOAD A FILE
        self.cmd(
            "az load test file upload "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--path "{test_plan}" '
        )

        #7 LIST FILES AND CHECK
        files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert self.kwargs["file_name"] in [file["fileName"] for file in files]

        #8 DOWNLOAD A FILE
        with tempfile.TemporaryDirectory(
            prefix="clitest-load-", suffix=create_random_name(prefix="", length=5)
        ) as temp_dir:
            self.kwargs.update({"download_path": temp_dir})

            self.cmd(
                "az load test file download "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--file-name {file_name} "
                '--path "{download_path}" '
            )

            assert os.path.exists(os.path.join(temp_dir, self.kwargs["file_name"]))
        
        #9 APP COMPONENT ADD AND LIST IT TO CHECK
        self.kwargs.update(
            {
                "app_component_id": storage_account_id,
                "app_component_name": storage_account_name,
                "app_component_type": storage_account_type,
                "app_component_kind": storage_account_kind,
            }
        )

        # TODO: Create an Azure resource for app component
        self.cmd(
            "az load test app-component add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-name "{app_component_name}" '
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" '
            '--app-component-kind "{app_component_kind}" ',
        ).get_output_in_json()

        app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        app_component = app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        assert app_component is not None and self.kwargs[
            "app_component_id"
        ] == app_component.get("resourceId")

        #10 SERVER METRIC ADD AND LIST IT TO CHECK
        self.kwargs.update(
            {
                "server_metric_id": LoadTestConstants.SERVER_METRIC_ID.format(storage_account_id),
                "server_metric_name": LoadTestConstants.SERVER_METRIC_NAME,
                "server_metric_namespace": LoadTestConstants.SERVER_METRIC_NAMESPACE,
                "aggregation": LoadTestConstants.AGGREGATION,
            }
        )
        self.cmd(
            "az load test server-metric add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--metric-id "{server_metric_id}" '
            '--metric-name " {server_metric_name}" '
            '--metric-namespace "{server_metric_namespace}" '
            "--aggregation {aggregation} "
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" ',
        ).get_output_in_json()

        server_metrics = self.cmd(
            "az load test server-metric list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        server_metric = server_metrics.get("metrics", {}).get(
            self.kwargs["server_metric_id"]
        )
        #11 REMOVE SERVER METRIC AND LIST IT TO CHECK
        assert server_metric is not None
        #assert self.kwargs[
        #    "server_metric_id"
        #] == server_metric.get("id")

        self.cmd(
            "az load test server-metric remove "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--metric-id "{server_metric_id}" '
            "--yes"
        )

        server_metrics = self.cmd(
            "az load test server-metric list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not server_metrics.get("metrics", {}).get(
            self.kwargs["server_metric_id"]
        )

        #12 REMOVE APP COMPONENT AND LIST IT TO CHECK
        self.cmd(
            "az load test app-component remove "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-id "{app_component_id}" '
            "--yes"
        )

        app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        #13 DELETE TEST
        self.cmd(
            "az load test delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes"
        )
        #14 LIST TESTS TO CHECK IF TEST IS DELETED
        tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] not in [test.get("testId") for test in tests]


    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_invalid(self, rg, load):
        #1. Create a test with already existing test id
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.INVALID_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )
        checks=[JMESPathCheck("testId", self.kwargs["test_id"]),
                    JMESPathCheck("loadTestConfiguration.engineInstances", 1),
                    JMESPathCheck("environmentVariables.rps", '10')]
        create_test(self)
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
            )
        except Exception as e:
            assert "Test with given test ID " in str(e)

        #2. Provide invalid path for load test config file
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--load-test-config-file "invalid_path.yaml" '
            )
        except Exception as e:
            assert "Provided path" in str(e)
        delete_test(self)

        #3. Update a test which doesnt exist
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.INVALID_UPDATE_TEST_ID,
            }
        )
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--engine-instances 11 ",
            )
        except Exception as e:
            msg = "Test with given test ID : "+LoadTestConstants.INVALID_UPDATE_TEST_ID+" does not exist"
            assert "Test with given test ID " in str(e)
        
        #4. INVALID PATH IN DOWNLOAD TEST CASE
        self.kwargs.update(
            {
                "path": r"\INVALID_PATH",
            }
        )
        try:
            self.cmd(
                "az load test download-files "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--path "{path}"'
            )
        except Exception as e:
            assert "Provided path" in str(e)

        self.kwargs.update(
            {
                "certificate": LoadTestConstants.MULTIPLE_CERTIFICATE,
                "secret": LoadTestConstants.INVALID_SECRET,
                "env": LoadTestConstants.INVALID_ENV,
            }
        )
        
        #5 Multiple certificate check
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--certificate "{certificate}" '
            )
        except Exception as e:
            assert "Invalid Azure Key Vault Certificate URL:" in str(e)

        #6 Invalid secret check
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--secret "{secret}" '
            )
        except Exception as e:
            assert "Invalid Azure Key Vault Secret URL:" in str(e)

        #7 Invalid env check
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--env "{env}" '
            )
        except Exception as e:
            assert "Invalid env argument" in str(e)

        #8 Invalid subnet id check
        self.kwargs.update(
            {
                "subnet_id": LoadTestConstants.INVALID_SUBNET_ID,
            }
        )
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--subnet-id "{subnet_id}" '
            )
        except Exception as e:
            assert "not a valid Azure subnet resource ID" in str(e)

        #9 Invalid test plan file
        self.kwargs.update(
            {
                "test_plan": LoadTestConstants.ADDITIONAL_FILE
            }
        )
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--test-plan "{test_plan}" '
            )
        except Exception as e:
            assert "Invalid test plan file extension:" in str(e)
        
        #10 Invalid split csv
        self.kwargs.update(
            {
                "split_csv": "Random Text"
            }
        )
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--split-csv "{split_csv}" '
            )
        except Exception as e:
            assert "Invalid split-csv value:" in str(e)