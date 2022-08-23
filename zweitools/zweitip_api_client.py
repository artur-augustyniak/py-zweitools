#!/usr/bin/env python3

import logging


from typing import TypeAlias
logger = logging.getLogger(__name__)


RequestResult: TypeAlias = tuple[int, dict]


class ZapiClient(object):

    PATCH_SUCCESS_CODES = [201, 301]

    def __init__(self):
        pass

    def patch(self, event: dict, patch: dict) -> RequestResult:
        return 201, {"ok": 1}


if __name__ == '__main__':
    logger.critical("This is not the main module")
