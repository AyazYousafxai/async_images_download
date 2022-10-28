from email import message_from_binary_file, policy
from typing import List, Tuple, Optional
from urllib import request as ulreq
from email.parser import BytesParser
from async_images_download_from_email.email_scraping import Scraping
from bs4 import BeautifulSoup
from PIL import ImageFile
from email import policy
import eml_parser
import aiofiles
import argparse
import aiohttp
import asyncio
import json
import glob
import uuid
import os

scrap = Scraping()


async def async_download_image(image_url: str,
                               download_dir: str,
                               ) -> None:
    """download images and save in folder

    Args:
        image_url (str): image url from which image downlod
        download_dir (str): directory where image to save images
    """

    image_filename = image_url.split('/')[-1]
    image_filepath = os.path.join(download_dir, image_filename)
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                content = await response.read()
                async with aiofiles.open(image_filepath, "wb") as f:
                    await f.write(content)
            else:
                print(f"Unable to download image from {image_url}")


async def async_download_images(image_url_tuples: List,
                                download_dir: str) -> None:
    """create async corountines for every single url

    Args:
        image_url_tuples (List): list of images 
        download_dir (str): directory
    """

    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    coroutines = [
        async_download_image(image_url=image_url_tuple,
                             download_dir=download_dir)
        for image_url_tuple in image_url_tuples
    ]

    await asyncio.gather(*coroutines)


def extract_url_from_html(raw_text):
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


def main(eml_data_path):
    """ read email from dir one by one 

    Args:
        eml_data_path (str): path of folder where emails are store
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
                html = scrap.scraping_email_body(a.decode("utf-8"))
                images_link = extract_url_from_html(html)
                download_dir = "images/"+subject
                asyncio.run(
                    async_download_images(image_url_tuples=images_link,
                                          download_dir=download_dir))

            except Exception as e:
                print(e)


if __name__ == "__main__":
    eml_data_path = 'src/email'
    main(eml_data_path)
