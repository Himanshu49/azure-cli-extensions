from azext_load.data_plane.utils import argtypes


def load_arguments(self, _):
    # Load Test

    with self.argument_context("load test create") as c:
        c.argument("env", argtypes.env)
        c.argument("secrets", argtypes.secret)
        c.argument("certificate", argtypes.certificate)
        c.argument("test_description", argtypes.test_description)
        c.argument("test_plan", argtypes.test_plan)
        c.argument("subnet_id", argtypes.subnet_id)
        c.argument("load_test_config_file", argtypes.load_test_config_file)
        c.argument("key_vault_reference_identity", argtypes.key_vault_reference_identity)
        c.argument("display_name", argtypes.display_name)
        c.argument("engine_instances", argtypes.engine_instances)

    with self.argument_context("load test update") as c:
        c.argument("env", argtypes.env)
        c.argument("secrets", argtypes.secret)
        c.argument("certificate", argtypes.certificate)
        c.argument("test_description", argtypes.test_description)
        c.argument("test_plan", argtypes.test_plan)
        c.argument("subnet_id", argtypes.subnet_id)
        c.argument("load_test_config_file", argtypes.load_test_config_file)
        c.argument("key_vault_reference_identity", argtypes.key_vault_reference_identity)
        c.argument("display_name", argtypes.display_name)
        c.argument("engine_instances", argtypes.engine_instances)
    
    with self.argument_context("load test download-files") as c:
        c.argument("path", argtypes.path)
    #

    # Load Test App Components
    with self.argument_context("load test app-components") as c:
        c.argument("app_component_id", argtypes.app_component_id)
    
    with self.argument_context("load test app-components create") as c:
        c.argument("app_component_type", argtypes.app_component_type)
        c.argument("app_component_name", argtypes.app_component_name)
        c.argument("app_component_type", argtypes.app_component_type)
    #

    # Load Test Server Metrics
    with self.argument_context("load test server-metrics") as c:
        c.argument("metric_id", argtypes.metric_id)

    with self.argument_context("load test server-metrics add") as c:
        c.argument("metric_name", argtypes.metric_name)
        c.argument("metric_namespace", argtypes.metric_namespace)
        c.argument("aggregation", argtypes.aggregation)
        c.argument("app_component_id", argtypes.app_component_id)
        c.argument("app_component_type", argtypes.app_component_type)

    #