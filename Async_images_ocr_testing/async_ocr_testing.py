from subprocess import call
from types import coroutine
from typing import List
import aiohttp
import email
import asyncio
import os
import asyncio
from PIL import Image
import requests
from io import StringIO,BytesIO
from email import message_from_binary_file, policy
from typing import List, Tuple, Optional
from urllib import request as ulreq
from email.parser import BytesParser
from bs4 import BeautifulSoup
from PIL import ImageFile
from email import policy
import eml_parser
import aiofiles
import argparse
import aiohttp
import asyncio
import glob
import os
import time
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()  

FOLDER_PATH = "/home/xylexa/Youniq redfabric/easy_ocr_image_download/Async_images_ocr_testing/email"
REST_API = "http://127.0.0.1:8000/ocr/"

class AsyncEmailScraping:
    """
    """

    def __init__(self):
        """
        """
        self.body = None
        self.html = None
        self.images_url = []
    def __call__(self,
                 eml_data_path: str) -> list:
        """
        """
        for file_path in glob.glob(os.path.join(eml_data_path, '*.eml')):
            print('****************************************** next email ***************************************')
            with open(file_path) as f:
                with open(f.name, 'rb') as f:
                    a = f.read()
                    msg = BytesParser(policy=policy.default).parse(f)
                try:
                    eml = eml_parser.eml_parser.decode_email_b(a, True, True)
                    subject = eml['header']['subject']
                    log.info(subject)
                    ur = asyncio.run(self.scraping_email_body(a.decode("utf-8")))
                    # self.images_url.append(ur)
                    log.info('extract %s',self.images_url)
                except Exception as e:
                    log.info(e)
            self.images_url.append(ur)
            
        return self.images_url
    async def async_test(self):
       a = await asyncio.gather(
            asyncio.to_thread(self.scraping_email_body)
        )
       return a
    async def scraping_email_body(self, raw_email: str) -> list:
        """convert raw email to email format and extract body from email and convert it to html format


        Args:
            raw_email (str): raw emails

        Returns:
            html (str): extracted body from email
        """
        email_body = email.message_from_string(raw_email)
        del raw_email

        if email_body.is_multipart():
            for part in email_body.walk():
                content_type = part.get_content_type()
                disp = str(part.get('Content-Disposition'))
                # search plain text
                if part.get_content_charset() is None:
                    # if character set is unknown then decode something
                    self.body = part.get_payload(decode=True)
                    continue
                if content_type == 'text/plain' and 'attachment' not in disp:
                    charset = part.get_content_charset()
                    # decode base64 unicode bytestring into plain text
                    self.body = part.get_payload(decode=True).decode(
                        encoding=charset, errors="ignore")
                if content_type == 'text/html' and 'attachment' not in disp:
                    charset = part.get_content_charset()
                    self.html = part.get_payload(decode=True).decode(
                        encoding=charset, errors="ignore")
                    break
        else:
            # if email is not multi part
            content_type = email_body.get_content_type()
            if email_body.get_content_charset() is None:
                self.body = email_body.get_payload(decode=True)
            else:
                charset = email_body.get_content_charset()
                if content_type == 'text/plain':
                    self.body = email_body.get_payload(decode=True).decode(
                        encoding=charset, errors="ignore")
                if content_type == 'text/html':
                    self.html = email_body.get_payload(decode=True).decode(
                        encoding=charset, errors="ignore")
        if self.body:
            self.html = self.html

        u = await self.extract_url_from_html(self.html)
        return u
    async def extract_url_from_html(self,raw_text: str) -> list:
        """
            extract url from html which was extracted from email body 
        Args:
            raw_text (str): html of email body

        Returns:
            images_url (list): list of images urls
        """
        soup = BeautifulSoup(raw_text, "html.parser")
        images_url = []
        for img in soup.select('a[href] img'):
            try:
                images_url.append(img['src'])
            except Exception as e:
                pass
        return images_url
log.info('main')
asy_email = AsyncEmailScraping()
images = asy_email(FOLDER_PATH)
images = [i for img in images for i in img]
async def call_api(url: str) -> None:
    try:
        async with aiohttp.ClientSession() as session:
                start = time.time()
                async with session.get(REST_API,data={
                    "url":url
                    }) as resp:
                    log.info(resp.status)
                    if resp.status == 200:
                        content = await resp.read()
                        end = time.time()
                        log.info("response time %s of url %s", end - start,url)
                        log.info("text extracted %s ",content)
                    else:
                        # log.error(f"Unable to download image from {url}")
                        pass
    except Exception as e:
            log.info(e)

async def create_task(url_list: list) -> None:
    coroutine = [
        call_api(url) for url in url_list
        ]
    await asyncio.gather(*coroutine)

asyncio.run(create_task(images))

                

