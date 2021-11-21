from contextlib import suppress

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.utils.exceptions import BadRequest
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from loguru import logger
from src.telexkcdbot.keyboards import kboard
from src.telexkcdbot.databases.users_db import users_db
from src.telexkcdbot.databases.comics_db import comics_db
from src.telexkcdbot.common_utils import broadcast, suppressed_exceptions, remove_prev_message_kb
from src.telexkcdbot.config import ADMIN_ID, LOGS_DIR


admin_panel_text_base = "<b>*** ADMIN PANEL ***</b>\n"


class Broadcast(StatesGroup):
    waiting_for_input = State()


async def cmd_admin(msg: Message, state: FSMContext):
    if msg.from_user.id != int(ADMIN_ID):
        await msg.answer("❗ <b>For admin only!</b>")
    else:
        await remove_prev_message_kb(msg)
        await state.reset_data()

        await msg.answer(admin_panel_text_base,
                         reply_markup=await kboard.admin_panel())


async def cb_users_info(call: CallbackQuery):
    with suppress(*suppressed_exceptions):
        await call.message.delete()

    users_info = await users_db.get_admin_users_info()

    await call.message.answer(text=f"{admin_panel_text_base}"
                                   f"<b>Total</b>: <i>{users_info.users_num}</i>\n"
                                   f"<b>Active</b>: <i>{users_info.last_week_active_users_num}</i>\n"
                                   f"<b>In only-ru mode: </b>: <i>{users_info.only_ru_users_num}</i>\n",
                              reply_markup=await kboard.admin_panel())


async def cb_toggle_spec_status(call: CallbackQuery):
    last_comic_id, _ = await users_db.get_last_comic_info(ADMIN_ID)
    await comics_db.toggle_spec_status(last_comic_id)
    await call.message.edit_text(text=f"{admin_panel_text_base}❗ <b>It's done for {last_comic_id}.</b>",
                                 reply_markup=await kboard.admin_panel())


async def cb_send_log(call: CallbackQuery):
    filename = LOGS_DIR / 'actions.log' if 'actions' in call.data else LOGS_DIR / 'errors.log'

    try:
        await call.message.answer_document(InputFile(filename))
    except BadRequest as err:
        logger.error(f"Couldn't send logs ({err})")


async def cb_type_broadcast_message(call: CallbackQuery):
    await Broadcast.waiting_for_input.set()
    await call.message.answer("❗ <b>Type in a broadcast message (or /cancel):</b>")


async def cmd_cancel(msg: Message, state: FSMContext):
    if await state.get_state() is None:
        return

    await msg.answer("❗ <b>Canceled.</b>")
    await state.finish()


async def broadcast_admin_msg(msg: Message, state: FSMContext):
    await broadcast(text=f"❗ <u><b>ADMIN MESSAGE:\n</b></u>  {msg.text}")
    await state.finish()


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_admin, commands='admin')
    dp.register_callback_query_handler(cb_users_info, text='users_info')
    dp.register_callback_query_handler(cb_toggle_spec_status, text='change_spec_status')
    dp.register_callback_query_handler(cb_send_log, Text(startswith='send_'))
    dp.register_callback_query_handler(cb_type_broadcast_message, text='broadcast_admin_msg')
    dp.register_message_handler(cmd_cancel, commands='cancel', state=Broadcast.waiting_for_input)
    dp.register_message_handler(broadcast_admin_msg, state=Broadcast.waiting_for_input)
