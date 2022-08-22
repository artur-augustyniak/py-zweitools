#!/usr/bin/env python3
import logging
import validators
import urllib
import re
from IPy import IP
from enum import Enum
from schwifty import IBAN
logger = logging.getLogger(__name__)


class HashKind(Enum):
    UNK = r"UNK"
    MD5 = r"[a-fA-F0-9]{32}"
    SHA1 = r"[a-fA-F0-9]{40}"
    SHA256 = r"[a-fA-F0-9]{64}"


def is_hash(kind: HashKind, val: str) -> bool:
    return recog_hash(val) == kind


def recog_hash(hash: str) -> HashKind:
    for hk in HashKind:
        result = re.match("^" + hk.value + "$", hash)
        if result:
            return hk
    return HashKind.UNK


def is_email(email: str) -> bool:
    return validators.email(email)


def is_btc(btc: str) -> bool:
    return validators.btc_address(btc)


def is_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme is not None \
        and (validators.domain(parsed.netloc) == True)


def is_domain(d: str) -> bool:
    return validators.domain(d)


def cidr_to_netmask(cidr: str) -> str:
    cidr = int(cidr)
    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    return (str((0xff000000 & mask) >> 24) + '.' +
            str((0x00ff0000 & mask) >> 16) + '.' +
            str((0x0000ff00 & mask) >> 8) + '.' +
            str((0x000000ff & mask)))


def is_public_ipv4(ip: str, cidr=None) -> bool:
    '''
    If cidr is given network and broadcast are considered non-public
    49.51.136.17
    ip:     49.51.8.1/23
    net:    49.51.8.0/23
    range:  49.51.8.0-49.51.9.255
    '''
    try:
        ipy = IP(ip)
        net = []
        if cidr:
            nety = IP(
                "%s/%s" % (ip, cidr_to_netmask(cidr)),
                make_net=True
            )
            net.append(nety.net().strNormal() != ip)
            net.append(nety.broadcast().strNormal() != ip)

        ver = 4 == ipy.version()
        pub = "PUBLIC" == ipy.iptype()
        return all([ver, pub] + net)
    except ValueError:
        return False


if __name__ == '__main__':
    logger.critical("This is not the main module")
