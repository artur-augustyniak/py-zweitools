#!/usr/bin/env python3
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import logging
import requests
from typing import TypeAlias
from bravado_core.spec import Spec
from bravado_core.validate import validate_object
logger = logging.getLogger(__name__)


ValidationResult: TypeAlias = tuple[bool, str]


class EventValidator(object):

    _BRAVADO_CONFIG = {
        'validate_swagger_spec': False,
        'validate_requests': False,
        'validate_responses': False,
        'use_models': True,
    }

    def __init__(self, bravado_spec: Spec, target_definition: dict):
        self.bravado_spec = bravado_spec
        self.target_definition = target_definition

    @staticmethod
    def from_schema_url(url: str, definition_key: str,  validate_ssl=True) -> 'EventValidator':
        resp = requests.get(url, verify=validate_ssl)
        if resp.status_code == 200:
            spec_dict = resp.json()
            return EventValidator(
                Spec.from_dict(
                    spec_dict,
                    config=EventValidator._BRAVADO_CONFIG
                ),
                spec_dict['definitions'][definition_key]
            )
        else:
            msg = f"Failed to get spec from {url} with code {resp.status_code}"
            logger.error(msg)
            raise RuntimeError(msg)

    def is_valid(self, event: dict) -> ValidationResult:
        try:
            validate_object(self.bravado_spec, self.target_definition, event)
            return True, "Ok"
        except Exception as e:
            return False, str(e)


if __name__ == '__main__':
    logger.critical("This is not the main module")
