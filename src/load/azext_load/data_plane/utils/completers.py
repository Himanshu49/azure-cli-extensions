from azext_load.data_plane.utils.utils import get_admin_data_plane_client
from azure.cli.core.commands.parameters import Completer
from knack.log import get_logger

logger = get_logger(__name__)


def get_test_id_completion_list():
    @Completer
    def completer(cmd, prefix, namespace, **kwargs):  # pylint: disable=unused-argument
        load_test_resource = getattr(namespace, "load_test_resource", None)
        resource_group_name = getattr(namespace, "resource_group_name", None)

        if not load_test_resource or not resource_group_name:
            return []

        client = get_admin_data_plane_client(
            cmd, load_test_resource, resource_group_name
        )
        test_ids = [
            test.get("testId") for test in client.list_tests() if "testId" in test
        ]
        logger.debug("Test IDs list in Test ID completer: %s", test_ids)
        return test_ids

    return completer