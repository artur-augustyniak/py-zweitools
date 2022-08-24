#!/usr/bin/env python3
from abc import abstractmethod
import logging

logger = logging.getLogger(__name__)


class ZeventHandlerABC(object):

    @abstractmethod
    def handle(self, event: dict) -> None:
        pass


if __name__ == '__main__':
    logger.critical("This is not the main module")
