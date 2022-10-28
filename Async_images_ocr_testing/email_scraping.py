"""
Created on Tue Jul 13 14:20:24 2021

@author: xylexa
"""
import urllib.request
import email


class Scraping():
    def __init__(self):
        pass

    def scraping_email_body(self, raw_email):
        """convert raw email to email format and extract body from email and convert it to html format


        Args:
            raw_email (str): raw emails

        Returns:
            html (str): extracted body from email
        """
        email_body = email.message_from_string(raw_email)
        del raw_email
        body = None
        html = None
        if email_body.is_multipart():
            for part in email_body.walk():
                content_type = part.get_content_type()
                disp = str(part.get('Content-Disposition'))
                # search plain text
                if part.get_content_charset() is None:
                    # if character set is unknown then decode something
                    body = part.get_payload(decode=True)
                    continue
                if content_type == 'text/plain' and 'attachment' not in disp:
                    charset = part.get_content_charset()
                    # decode base64 unicode bytestring into plain text
                    body = part.get_payload(decode=True).decode(
                        encoding=charset, errors="ignore")
                if content_type == 'text/html' and 'attachment' not in disp:
                    charset = part.get_content_charset()
                    html = part.get_payload(decode=True).decode(
                        encoding=charset, errors="ignore")
                    break
        else:
            # if email is not multi part
            content_type = email_body.get_content_type()
            if email_body.get_content_charset() is None:
                body = email_body.get_payload(decode=True)
            else:
                charset = email_body.get_content_charset()
                if content_type == 'text/plain':
                    body = email_body.get_payload(decode=True).decode(
                        encoding=charset, errors="ignore")
                if content_type == 'text/html':
                    html = email_body.get_payload(decode=True).decode(
                        encoding=charset, errors="ignore")
        if html:
            return html
        elif body:
            return body

        return ''
