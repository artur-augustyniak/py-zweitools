#!/usr/bin/env python3

import logging
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class EmailNotifier(object):

    def __init__(
        self,
        server: str,
        port: int,
        login: str,
        passw: str
    ) -> None:
        self.server = server
        self.port = port
        self.login = login
        self.passw = passw

    def send_email(
        self,
        bcc_rcpnts: list[str],
        subject: str,
        body_plain: str = None,
        body_html: str = None,
        attachment_paths: list[str] = []
    ) -> None:

        if body_html is None and body_plain is None:
            msg = "No email body provided"
            logger.critical(msg)
            raise RuntimeError(msg)

        message = MIMEMultipart()
        message["Subject"] = subject
        message['From'] = self.login
        message["Bcc"] = ", ".join(bcc_rcpnts)

        if body_plain is not None:
            plain = MIMEText(body_plain, "plain")
            plain.set_charset("utf-8")
            message.attach(plain)
        if body_html is not None:
            html = MIMEText(body_html, 'html')
            html.set_charset("utf-8")
            message.attach(html)

        if attachment_paths:
            for ap in attachment_paths:
                with open(ap, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition", "attachment; filename= %s" % os.path.basename(ap))
            message.attach(part)
        conn = SMTP(self.server, self.port)
        conn.login(self.login, self.passw)
        try:
            conn.sendmail(self.login, bcc_rcpnts, message.as_string())
            logger.info(f"email {subject} sent")
        finally:
            conn.close()


if __name__ == '__main__':
    logger.critical("This is not the main module")
