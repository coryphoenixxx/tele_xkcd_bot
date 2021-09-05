# This file not use in app
# it's only for extracting russian comics data
# from xkcd_ru_tg_channel.html (get from "fully scrolled" https://t.me/s/xkcdru).
# The images urls are relevant only for a day!

import re
import json
import aiofiles
import aiofiles.os
import aiohttp
import asyncio
from tqdm import tqdm

from bs4 import BeautifulSoup
from bs4.element import NavigableString


async def get_image_path(comic_id: str, img_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        response = await session.get(img_url)
        if response.ok:
            filepath = f"img/aux_ru_comic_images/{comic_id}__ru_version.jpg"
            async with aiofiles.open(filepath, mode='wb') as f:
                await f.write(await response.read())
            return filepath[4:]
        else:
            print(f"Couldn't download {comic_id}")


async def main():
    with open("xkcd_ru_tg_channel.html", 'rb') as fp:
        soup = BeautifulSoup(fp, 'lxml')

    messages = soup.find_all('div', class_='tgme_widget_message js-widget_message')

    ru_comic_data_dict = {}

    for msg in tqdm(messages):
        footer = msg.find_all('div', {'class': 'tgme_widget_message_text'})
        contents = footer[0].contents

        try:
            ru_title = contents[0].text
        except Exception as err:
            print(err)
            continue

        if ru_title.endswith('.'):
            ru_title = ru_title[:-1]

        nav_tags = list(filter(lambda x: type(x) == NavigableString, contents))

        comic_id = nav_tags[-1].strip()[1:]

        if comic_id in ru_comic_data_dict.keys():
            continue

        ru_comment = ' '.join(nav_tags[:-1])
        ru_comment = ru_comment.replace('>', '')

        style_text = msg.find_next('a', class_='tgme_widget_message_photo_wrap')['style']
        ru_img_url = re.search('\(\'(.*)\'\)', style_text).group(1)
        new_ru_img_url = await get_image_path(comic_id, ru_img_url)

        ru_comic_data_dict[comic_id] = {'ru_title': ru_title,
                                        'ru_img_url': new_ru_img_url,
                                        'ru_comment': ru_comment}

    with open('aux_ru_comic_data.json', 'w', encoding='utf8') as f:
        json.dump(ru_comic_data_dict, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
