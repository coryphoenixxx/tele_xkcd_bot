import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified, MessageToEditNotFound, MessageCantBeEdited
from aiogram.types import Message
from contextlib import suppress

from src.telexkcdbot.bot import bot
from src.telexkcdbot.databases.users import users_db
from src.telexkcdbot.databases.comics import comics_db
from src.telexkcdbot.utils import send_comic, cyrillic, punctuation, make_headline
from src.telexkcdbot.keyboards import kboard


suppress_exceptions = (AttributeError, MessageNotModified, MessageToEditNotFound, MessageCantBeEdited)


def cut_into_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def remove_kb_of_prev_message(msg: Message):
    with suppress(*suppress_exceptions):
        await bot.edit_message_reply_markup(msg.from_user.id, msg.message_id - 1)


async def is_cyrillic(text: str) -> bool:
    return set(text).issubset(cyrillic + punctuation)


async def send_comics_list_as_text(user_id: int, comics_list: list):
    for chunk in cut_into_chunks(comics_list, 35):
        headlines = []
        for comic_id, title, img_url in chunk:
            headlines.append(await make_headline(comic_id, title, img_url))
        text = '\n'.join(headlines)
        await bot.send_message(user_id, text, disable_web_page_preview=True)
        await asyncio.sleep(0.8)


async def send_user_bookmarks(user_id: int, message_id: int, state: FSMContext, keyboard=None):
    # TODO: what if 1 bookmarks
    bookmarks_list = await users_db.get_bookmarks(user_id)
    _len = len(bookmarks_list)

    if not _len:
        text = f"❗ <b>You have no bookmarks.\nYou can bookmark a comic with the ❤ press.</b>"
        if keyboard:
            await bot.send_message(user_id, text, reply_markup=keyboard)
        else:
            await bot.send_message(user_id, text, reply_markup=await kboard.menu_or_xkcding(user_id))

    else:
        await bot.send_message(user_id, f"❗ <b>You have <u><b>{_len}</b></u> bookmarks</b>:")

        comics_ids, titles, img_urls = [], [], []
        for comic_id in bookmarks_list:
            comic_data = await comics_db.get_comic_data_by_id(comic_id)
            comics_ids.append(comic_data[0])
            titles.append(comic_data[1])
            img_urls.append(comic_data[2])

        await send_comics_list_as_text(user_id, comics_list=[comics_ids, titles, img_urls])
        await state.update_data(list=bookmarks_list)

        await trav_step(user_id, message_id, state)


async def send_menu(user_id: int):
    help_text = """<b>*** MENU ***</b>

Type in the <u><b>number</b></u> and I'll find a comic with this number!
Type in the <u><b>word</b></u> and I'll find comics whose titles contains this word! 


<u><b>In menu you can:</b></u>
— subscribe for the new comic release <i>(every Mon, Wed and Fri USA time)</i>.
— read comics from your bookmarks.
— remove language button <i>(under the comic, which have russian translation)</i> if you don't need it.
— start xkcding!

If the sound of the notification annoys you, you can <b><u>mute</u></b> the telexkcdbot 
<i>(click on the three dots in the upper right corner)</i>.


❗❗❗
If something goes wrong or looks strange try to view a comic in your browser <i>(I'll give you a link)</i>."""

    await bot.send_message(user_id, help_text, reply_markup=await kboard.menu(user_id), disable_notification=True)


async def trav_step(user_id: int, message_id: int, state: FSMContext):
    list_ = (await state.get_data()).get('list')

    if not list_:
        await trav_stop(user_id, message_id, state)
    else:
        lang = (await state.get_data()).get('lang')
        comic_lang = 'en' if not lang else 'ru'
        comic_data = await comics_db.get_comic_data_by_id(list_.pop(0), comic_lang=comic_lang)

        if list_:
            await send_comic(user_id, comic_data=comic_data, keyboard=kboard.traversal, comic_lang=comic_lang)
            await state.update_data(list=list_)
        else:
            await send_comic(user_id, comic_data=comic_data, keyboard=kboard.navigation, comic_lang=comic_lang)
            await state.reset_data()


async def trav_stop(user_id: int, message_id: int, state: FSMContext):
    comic_id, comic_lang = await users_db.get_cur_comic_info(user_id)
    with suppress(*suppress_exceptions):
        await bot.edit_message_reply_markup(user_id,
                                            message_id=message_id,
                                            reply_markup=await kboard.navigation(user_id, comic_id, comic_lang))
    await state.reset_data()


def rate_limit(limit: int, key=None):
    """
    Decorator for configuring rate limit and key in different functions.
    """
    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func
    return decorator
