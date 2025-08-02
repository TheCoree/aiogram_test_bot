from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.database.requests import get_categories, get_items_by_category

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Товары', callback_data='categories')]
])

async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='На Главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def item_navigation(category_id: int, index: int, total: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀ Назад", callback_data=f"item_{category_id}_{index - 1}"))
    if index < total - 1:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶", callback_data=f"item_{category_id}_{index + 1}"))

    if nav_buttons:
        kb.row(*nav_buttons)

    kb.row(InlineKeyboardButton(text="На главную", callback_data="to_main"))

    return kb.as_markup()