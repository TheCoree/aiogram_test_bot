from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from app.middlewares import TestMiddleware
import app.keyboards as kb

import app.database.requests as rq

router = Router()

class ItemBrowsing(StatesGroup):
    browsing = State()

# Стартовые хендлеры и колбек куери для него
@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Добро пожаловать в магазин техники CORE TECH! Тут вы сможете потратить свои TON!', reply_markup=kb.main)

@router.callback_query(F.data == 'to_main')
async def to_main_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer('Добро пожаловать в магазин техники CORE TECH! Тут вы сможете потратить свои TON!', reply_markup=kb.main)
    await state.clear()



@router.callback_query(F.data == 'categories')
async def categories(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Выберите картегорую товара', reply_markup=await kb.categories())

@router.callback_query(F.data.startswith("category_"))
async def show_first_item(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    items = list(await rq.get_items_by_category(category_id))

    if not items:
        await callback.message.edit_text("В этой категории нет товаров.")
        return

    await state.set_state(ItemBrowsing.browsing)
    await state.update_data(items=items, category_id=category_id)

    item = items[0]

    try:
        await callback.bot.edit_message_media(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=item.image_url,
                caption=f"<b>{item.name}</b>\n\n{item.description}\n\nЦена: {item.price}TON",
                parse_mode="HTML"
            ),
            reply_markup=await kb.item_navigation(category_id, 0, len(items))
        )
    except TelegramBadRequest:
        # Если по какой-то причине не удалось отредактировать — удаляем и отправляем заново
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=item.image_url,
            caption=f"<b>{item.name}</b>\n\n{item.description}\n\nЦена: {item.price} TON",
            reply_markup=await kb.item_navigation(category_id, 0, len(items)),
            parse_mode="HTML"
        )




@router.callback_query(F.data.startswith("item_"))
async def turn_item_page(callback: CallbackQuery, state: FSMContext):
    _, cat_id, index = callback.data.split("_")
    category_id = int(cat_id)
    index = int(index)

    data = await state.get_data()
    items = data.get("items")

    if not items:
        items = list(await rq.get_items_by_category(category_id))
        await state.update_data(items=items)

    item = items[index]

    try:
        # Попытка редактировать фото (если оно было)
        await callback.bot.edit_message_media(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=item.image_url,
                caption=f"<b>{item.name}</b>\n\n{item.description}\n\nЦена: {item.price} TON",
                parse_mode="HTML"
            ),
            reply_markup=await kb.item_navigation(category_id, index, len(items))
        )
    except TelegramBadRequest:
        # Если не получилось (например, сообщение было не фото) — удаляем и отправляем заново
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=item.image_url,
            caption=f"<b>{item.name}</b>\n\n{item.description}\n\nЦена: {item.price} TON",
            reply_markup=await kb.item_navigation(category_id, index, len(items)),
            parse_mode="HTML"
        )

    await callback.answer()
