#!/usr/bin/env python3
import logging
import requests
from datetime import datetime as dt
import json
from http import HTTPStatus as HS
from enum import Enum
from typing import TypeAlias, Iterable
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)


RequestResult: TypeAlias = tuple[int, dict]


class SortOrder(Enum):
    ASC = "+"
    DESC = "-"


class DateOP(Enum):
    LTE = "lte"
    GTE = "gte"
    EQ = "eq"
    NE = "ne"


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


class SearchDescriptor(object):

    def __init__(self) -> None:
        self.params = {}
        self.sort("_id")

    def offset(self, o: int) -> "SearchDescriptor":
        self.params['offset'] = o
        return self

    def limit(self, l: int) -> "SearchDescriptor":
        self.params['limit'] = l
        return self

    def sort(self, by_field: str, order: SortOrder = SortOrder.DESC) -> "SearchDescriptor":
        self.params['sort'] = f"{order.value}{by_field}"
        return self

    def add_filter(self, field: str, val: str) -> "SearchDescriptor":
        current_filters = self.params.get("filtering", [])
        current_filters.append(field)
        current_filters.append(val)
        self.params['filtering'] = current_filters
        return self

    def shape(self, fields: list[str], include=True) -> "SearchDescriptor":
        self.params['shape'] = fields
        self.params['shape_mode'] = 'true' if include else 'false'
        return self

    def filtering_params(self,
                         ignore_case: bool = False,
                         whole_word: bool = True,
                         force_and: bool = False
                         ) -> "SearchDescriptor":
        self.params['ignore_case'] = 'true' if ignore_case else 'false'
        self.params['whole_word'] = 'true' if whole_word else 'false'
        self.params['force_and'] = 'true' if force_and else 'false'

        return self

    def local_time_created_at(self, date_time: dt, op: DateOP) -> "SearchDescriptor":
        lte_date_str = date_time.strftime("%Y-%m-%dT%H:%M:%S")
        self.params['created_at'] = f"{op.value},{lte_date_str}"
        return self

    def local_time_updated_at(self, date_time: dt, op: DateOP) -> "SearchDescriptor":
        lte_date_str = date_time.strftime("%Y-%m-%dT%H:%M:%S")
        self.params['updated_at'] = f"{op.value},{lte_date_str}"
        return self

    def to_dict(self) -> dict:
        filtering = self.params.get('filtering', None)
        if filtering is not None:
            self.params['filtering'] = ",".join(filtering)

        shape = self.params.get("shape", None)
        if shape is not None:
            self.params['shape'] = ",".join(shape)
        return self.params


class ZapiClient(object):

    CLEINT_ERROR_CODES = list(map(lambda e: e.value, [HS.IM_A_TEAPOT]))
    PATCH_SUCCESS_CODES = list(map(lambda e: e.value, [HS.OK, HS.CONFLICT]))
    GET_SUCCESS_CODES = list(map(lambda e: e.value, [HS.OK]))

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

    def get_many(self, endpoint: ZapiEndpoint, search_params: SearchDescriptor = None) -> RequestResult:
        if search_params is None:
            params = {}
        else:
            params = search_params.to_dict()
        logger.debug(params)
        url = f"{self.base_url}{endpoint.value}/"
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            verify=self.verify_cert
        )

        return response.status_code, response.json()

    def get_results_iterator(self, endpoint: ZapiEndpoint, search_params: SearchDescriptor = None) -> Iterable[dict]:
        if search_params is None:
            params = {}
        else:
            params = search_params.to_dict()
        if params.get("limit") or params.get("offset"):
            logger.warning(
                "in iterator mode your limit and offset search params will be ignored")
        per_page = 300
        offset = 0
        while True:
            params['limit'] = per_page,
            params['offset'] = offset

            url = f"{self.base_url}{endpoint.value}/"
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                verify=self.verify_cert
            )

            status, response = response.status_code, response.json()

            if status not in ZapiClient.GET_SUCCESS_CODES:
                msg = f"iterator mode cannot fetch data for {endpoint.value} staus code {status} msg {str(response)}"
                logger.error(msg)
                return []
            else:
                items = response.get("results", [])
                for item in items:
                    yield item

                if len(items) < per_page:
                    break
                offset += per_page

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
            return HS.IM_A_TEAPOT.value, {"error": msg}


if __name__ == '__main__':
    logger.critical("This is not the main module")
