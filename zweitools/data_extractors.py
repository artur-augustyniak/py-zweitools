#!/usr/bin/env python3
from typing import TypeAlias
import logging
import requests
import asyncio
import tldextract
import zweitools.data_validators as dv
import re
logger = logging.getLogger(__name__)


DomainInfo: TypeAlias = tuple[tldextract.tldextract.ExtractResult, str]


def extract_domain_info(url_or_domain: str) -> DomainInfo:
    if not dv.is_url(url_or_domain) and not dv.is_domain(url_or_domain):
        return None, f"{url_or_domain} is not a url nor a domain"
    tldex = tldextract.extract(url_or_domain)
    return tldex, "ok"


def extract_hashtags(text: str) -> list[str]:
    hashtags = re.findall(r"#(\w+)", text)
    return list(set(hashtags))


def extract_user_refs(text: str) -> list[str]:
    hashtags = re.findall(r"@(\w+)", text)
    return list(set(hashtags))


async def follow_redirection(url: str, timeout: int) -> str:
    def exec_thunk():
        try:
            logger.debug(f"following redir for {url}")
            resulting = requests.get(
                url, timeout=timeout, verify=False).url.strip("\"'/")
            logger.debug(f"resulting redir for {url} result {resulting}")
            if url != resulting:
                return resulting
            else:
                return None
        except Exception as e:
            logger.warning(
                f"cannot follow url redir from {url} with error {str(e)}")
            return None
    loop = asyncio.get_event_loop()
    exec_future = loop.run_in_executor(None, exec_thunk)
    result = await exec_future
    return result if result is not None else url


def extract_urls(text: str, follow=False, timeout=10) -> list[str]:
    ret_urls = []
    pattern = r"(?P<url>https?://[^\s]+)"
    urls = re.findall(pattern, text)
    for url in urls:
        url = re.sub(r" ?[,'\"]", "", url).strip("\"'/")
        if dv.is_url(url):
            ret_urls.append(url)
    if follow:
        loop = asyncio.get_event_loop()
        ret_urls = list(set(ret_urls))
        tasks = []
        for u in ret_urls:
            tasks.append(follow_redirection(u, timeout=timeout))
        resulting_urls = loop.run_until_complete(
            asyncio.gather(*tasks)
        )
        ret_urls += resulting_urls
    return list(set(ret_urls))


def extract_hashes(text: str) -> list[dict]:
    resulting_hashes = []
    sha256list = list(set(re.findall(dv.HashKind.SHA256.value, text)))
    resulting_hashes += sha256list
    hashes_concat = "".join(resulting_hashes)
    for sha1 in re.findall(dv.HashKind.SHA1.value, text):
        if sha1 not in hashes_concat:
            resulting_hashes.append(sha1)
    hashes_concat = "".join(list(set(resulting_hashes)))
    for md5 in re.findall(dv.HashKind.MD5.value, text):
        if md5 not in hashes_concat:
            resulting_hashes.append(md5)
    resulting_hashes = list(set(resulting_hashes))
    res = []
    for h in resulting_hashes:
        res.append({
            "kind": dv.recog_hash(h).name.lower(),
            "value": h
        })
    return res


def extract_domains(text: str) -> list[str]:
    found = []
    pattern = r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}'
    domains = re.findall(pattern, text)
    for d in domains:
        if dv.is_domain(d):
            found.append(d)

    return list(set(found))


def extract_ips(text: str) -> list[str]:
    found = []
    ips = re.findall(r"(?P<ips>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text)
    for ip in ips:
        if dv.is_public_ipv4(ip):
            found.append(ip)

    return list(set(found))


def extract_nrbs(text: str) -> list[str]:
    found = []
    nrbs = re.findall(r'([0-9]{2}(?:[ \-]?[0-9]{4}){6})', text)
    for nrb in nrbs:
        nrb = nrb.replace(" ", "")
        if nrb[0].isdigit():
            nrb = "PL" + nrb
        try:
            iban = IBAN(nrb)
            found.append(nrb)
        except Exception as e:
            logger.warning(f"nrb validation error {nrb} {str(e)}")

    ibans = re.findall(
        r'[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}(?:[a-zA-Z0-9]?){0,16}', text.replace(" ", ""))
    for iban in ibans:
        if iban[2:] not in nrbs:
            found.append(iban)
    return list(set(found))


def extract_phones(text: str) -> list[str]:
    found = []
    #  would recommend to use the phonenumbers package which is a python port of Google's libphonenumber which includes a data set of mobile carriers now:

    # import phonenumbers
    # from phonenumbers import carrier
    # from phonenumbers.phonenumberutil import number_type

    # number = "+49 176 1234 5678"
    # carrier._is_mobile(number_type(phonenumbers.parse(number)))

    # phones = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
    # for p in phones:
    #     found.append(p)
    return list(set(found))


def extract_pii(text: str) -> list[object]:
    ret = []
    emails = list(
        set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)))
    for e in emails:
        if dv.is_email(e):
            ret.append({
                "kind": "pii_email",
                "value": e
            })

    # username:pass pair
    # pid
    # i inne
    return ret


def extract_btc(text: str) -> list[str]:
    # dv.is_btc(value)
    return []


if __name__ == '__main__':
    logger.critical("This is not the main module")
