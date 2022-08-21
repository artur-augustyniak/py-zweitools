#!/usr/bin/env python3
import logging
import requests
import asyncio
import zweitools.data_validators as dv
import re
from schwifty import IBAN
logger = logging.getLogger(__name__)


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
            resulting = requests.get(url, timeout=timeout).url.strip("\"'/")
            logger.debug(f"resulting redir for {url} id {resulting}")
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


def extract_urls(text: str, follow=False, timeout=3) -> list[str]:
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


def extract_md5s(text: str) -> list[str]:
    return ["md5"]

#   tweet_body = ioc_fanger.fang(
#         body.replace("[", "").replace("]", ""))
#     resulting_hashes = []
#     sha256list = list(set(re.findall(HashKind.SHA256.value, tweet_body)))
#     resulting_hashes += sha256list
#     hashes_concat = "".join(resulting_hashes)
#     for sha1 in re.findall(HashKind.SHA1.value, tweet_body):
#         if sha1 not in hashes_concat:
#             resulting_hashes.append(sha1)
#     hashes_concat = "".join(list(set(resulting_hashes)))
#     for md5 in re.findall(HashKind.MD5.value, tweet_body):
#         if md5 not in hashes_concat:
#             resulting_hashes.append(md5)
#     resulting_hashes = list(set(resulting_hashes))

def extract_sha1s(text: str) -> list[str]:
    return ["sha1"]


def extract_sha256s(text: str) -> list[str]:
    return ["sha266"]


if __name__ == '__main__':
    logger.critical("This is not the main module")

   # phone numbers pids

#   def expand_domains(self):
#         pattern = r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}'
#         found_STUB = "EXTRACTED_DOMAIN"
#         domains = re.findall(pattern, self.entity)
#         for d in domains:
#             if True:
#                 self.append_child(
#                     make_netloc(d),
#                     BaseEntityType.PERMANENT_ENTITY
#                 )
#         self.entity = re.sub(pattern, found_STUB, self.entity)


#    def expand_ips(self):
#         ips = re.findall(
#             r"(?P<ips>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", self.entity)
#         for ip in ips:
#             if is_public_ipv4(ip):
#                 self.append_child(
#                     make_netloc(ip),
#                     BaseEntityType.PERMANENT_ENTITY
#                 )

#     def expand_nrbs(self):
#         # nrbs = re.findall(r'\d{26}', self.entity.replace(" ", ""))
#         nrbs = re.findall(r'([0-9]{2}(?:[ \-]?[0-9]{4}){6})', self.entity)

#         # nrbs = re.findall(
#         #     r"([0-9]{2})(?=(?:[ \-]?[A-Z0-9]){9,30}$)((?:[ \-]?[A-Z0-9]{3,5}){2,7})([ \-]?[A-Z0-9]{1,3})?$", self.entity)

#         for nrb in nrbs:

#             nrb = nrb.replace(" ", "")
#             if nrb[0].isdigit():
#                 nrb = "PL" + nrb
#             try:
#                 iban = IBAN(nrb)
#                 self.append_child(
#                     NRB(nrb),
#                     BaseEntityType.PERMANENT_ENTITY
#                 )
#             except Exception as e:
#                 logger.warn("NRB VALIDATION ERROR %s %s" % (nrb, str(e)))


#         ibans = re.findall(
#             r'[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}(?:[a-zA-Z0-9]?){0,16}', self.entity.replace(" ", ""))
#         for iban in ibans:
#             if iban[2:] not in nrbs:
#                 self.append_child(
#                     NRB(iban),
#                     BaseEntityType.PERMANENT_ENTITY
#                 )
