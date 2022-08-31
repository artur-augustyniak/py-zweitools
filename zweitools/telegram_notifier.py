#!/usr/bin/env python3

import logging
from telegram_notifier import set_config_options, send_message
import re
logger = logging.getLogger(__name__)


MSG = '''
*###SUBJECT###*


```json
###BODY####
```
'''


class TelegramNotifier(object):

    def __init__(self, bot_token: str) -> None:
        self.bot_token = bot_token

    def notify(self, chat_id: str,  subject: str, body: str) -> None:
        set_config_options(chat_id=chat_id, token=self.bot_token)
        msg = MSG.replace("###SUBJECT###", re.escape(subject)).replace(
            "###BODY####", body)
        res = send_message(msg,  parse_mode="MarkdownV2")
        if res.status_code != 200:
            logger.error(
                f"cannot send telegram notification chat id {chat_id} error {res.status_code} {res.text}")


if __name__ == '__main__':
    logger.critical("This is not the main module")
