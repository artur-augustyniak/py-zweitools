#!/usr/bin/env python3

import logging
import requests
import json
from http import HTTPStatus as HS
from enum import Enum
from typing import TypeAlias
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)


RequestResult: TypeAlias = tuple[int, dict]


class ZapiEndpoint(Enum):
    PHISHING_DOMAIN = "/api/v1.0/phishing/domain"
    MISC_STRING = "/api/v1.0/misc/string"
    MISC_DATA = "/api/v1.0/misc/data"
    PII_BLIK = "/api/v1.0/pii/blik"
    PII_PHONE = "/api/v1.0/pii/phone"
    PII_CARD = "/api/v1.0/pii/card"
    PII_LOGIN = "/api/v1.0/pii/login"
    APK_SIGNATURE = "/api/v1.0/apk/signature"
    APK_NAMELIST = "/api/v1.0/apk/namelist"
    ARTIFACT_REPORT = "/api/v1.0/artifact/report"


class ZapiClient(object):

    CLEINT_ERROR_CODES = [HS.IM_A_TEAPOT]
    PATCH_SUCCESS_CODES = [HS.OK, HS.CONFLICT]

    def __init__(self,
                 api_key: str,
                 verify_cert: bool = True,
                 base_url: str = "https://yaftip.com"
                 ):
        self.base_url = base_url
        self.verify_cert = verify_cert
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-API-Key': api_key,
        }

    def patch(self,
              endpoint: ZapiEndpoint,
              event: dict,
              patch: dict
              ) -> RequestResult:
        try:
            e_id = event.get('_id', "nx")
            url = f"{self.base_url}{endpoint.value}/{e_id}"
            _ = patch.pop("_id", None)
            _ = patch.pop("updated_at", None)
            _ = patch.pop("created_at", None)
            response = requests.patch(
                url,
                headers=self.headers,
                data=json.dumps(patch),
                verify=self.verify_cert
            )
            return response.status_code, response.json()
        except Exception as e:
            msg = f"ZapiClient internal error for event {e_id} {str(e)}"
            logger.critical(msg, exc_info=True)
            return HS.IM_A_TEAPOT, {"error": msg}


if __name__ == '__main__':
    logger.critical("This is not the main module")
