#!/usr/bin/env python3

import logging


logger = logging.getLogger(__name__)


class ZrabbitClient(object):

    def __init__(self):
        pass

    def requeue_error(self, event: dict, msg: str) -> None:
        pass


if __name__ == '__main__':
    logger.critical("This is not the main module")
