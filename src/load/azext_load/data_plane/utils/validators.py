import re

from msrestazure.tools import is_valid_resource_id


def validate_test_id(namespace):
    if not isinstance(namespace.test_id, str):
        raise ValueError("Invalid test-id value")
    if not re.match("^[a-z0-9_-]*$", namespace.test_id):
        raise ValueError("Invalid test-id value")


def _validate_akv_url(string, type="secrets|certificates|keys|storage"):
    regex = f"^https://[a-zA-Z0-9_-]+\\.(?:vault|vault-int)\\.(?:azure|azure-int|usgovcloudapi|microsoftazure)\\.(?:net|cn|de)/(?:{type})/[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+|$)$"
    return re.match(regex, string, re.IGNORECASE)


def validate_env_vars(namespace):
    """Extracts multiple space-separated env vars in key[=value] format"""
    if isinstance(namespace.env, list):
        env_vars_dict = {}
        for item in namespace.env:
            env_vars_dict.update(_validate_env_var(item))
        namespace.env = env_vars_dict


def _validate_env_var(string):
    """Extracts a single env var in key[=value] format"""
    result = {}
    if string:
        comps = string.split("=", 1)
        result = {comps[0]: comps[1]} if len(comps) > 1 else {string: ""}
    return result


def validate_secrets(namespace):
    """Extracts multiple space-separated secrets in key[=value] format"""
    if isinstance(namespace.secrets, list):
        secrets_dict = {}
        for item in namespace.secrets:
            secrets_dict.update(_validate_secret(item))
        namespace.secrets = secrets_dict


def _validate_secret(string):
    """Extracts a single secret in key[=value] format"""
    result = {}
    if string:
        comps = string.split("=", 1)
        if not _validate_akv_url(comps[1], "secrets"):
            raise ValueError(f"Invalid AKV Secret URL: {string}")
        result = (
            {comps[0]: {"type": "AKV_SECRET_URI", "value": comps[1]}}
            if len(comps) > 1
            else {string: ""}
        )
    return result


def validate_certificate(namespace):
    """Extracts single certificate in key[=value] format"""
    if namespace.certificate is None:
        return
    if isinstance(namespace.certificate, list):
        if len(namespace.certificate) > 1:
            raise ValueError("Only one certificate is supported")
        certificate = namespace.certificate[0]
    elif isinstance(namespace.certificate, str):
        certificate = namespace.certificate
    else:
        raise ValueError(
            f"Invalid certificate value type: {type(namespace.certificate)}"
        )
    comps = certificate.split("=", 1)
    if not _validate_akv_url(comps[1], "certificates"):
        raise ValueError(f"Invalid AKV Certificate URL: {comps[1]}")
    namespace.certificate = {
        "name": comps[0],
        "type": "AKV_CERT_URI",
        "value": comps[1],
    }


def validate_app_component_id(namespace):
    if not isinstance(namespace.app_component_id, str):
        raise ValueError(
            f"Invalid app-component-id type: {type(namespace.app_component_id)}"
        )
    if not is_valid_resource_id(namespace.app_component_id):
        raise ValueError(
            f"app-component-id is not a valid Azure Resource ID: {namespace.app_component_id}"
        )
    # /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/{providerName}/components/{resourceName}"
    providerName = namespace.app_component_id.split("/")[5].casefold()
    if providerName != namespace.app_component_type.casefold():
        raise ValueError(
            f"Type of app-component-id and app-component-type mismatch: {providerName} vs {namespace.app_component_type}"
        )


def validate_metric_id(namespace):
    if not isinstance(namespace.metric_id, str):
        raise ValueError(f"Invalid metric-id type: {type(namespace.metric_id)}")
    if not is_valid_resource_id(namespace.metric_id):
        raise ValueError(
            f"metric-id is not a valid Azure Resource ID: {namespace.metric_id}"
        )
    if "metrics" not in namespace.metric_id.casefold():
        raise ValueError(
            f"Provided Azure Resource ID is not a valid server metrics resource: {namespace.metric_id}"
        )