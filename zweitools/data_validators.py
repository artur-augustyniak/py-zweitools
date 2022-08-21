#!/usr/bin/env python3
import logging
import validators
import urllib
logger = logging.getLogger(__name__)


# class HashKind(Enum):
#     MD5 = r"^[a-fA-F0-9]{32}$"
#     SHA1 = r"^[a-fA-F0-9]{40}$"
#     SHA256 = r"^[a-fA-F0-9]{64}$"


# def recog_hash(val):
#     for hk in HashKind:
#         result = re.match(hk.value, val)
#         if result:
#             logger.info("hash recog ok: %s is %s" % (val, hk.name))
#             return hk
#     logger.warning("hash recog fail: %s is not known hash format" % (val))
#     return "UNK"



def is_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme is not None \
        and (validators.domain(parsed.netloc) == True)


if __name__ == '__main__':
    logger.critical("This is not the main module")
