from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.services.template_manager import template_manager, DEFAULT_TEMPLATES
from src.utils.config import config
import json

router = Router()

class ContentState(StatesGroup):
    waiting_for_template_key = State()
    waiting_for_new_text = State()
    waiting_for_new_media = State()

def is_admin(user_id: int):
    return user_id in config.admins

@router.message(Command("content"))
async def list_content(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    text = "📝 **Управление контентом**\n\nВыберите шаблон для редактирования:\n"
    
    keyboard = []
    for key, val in DEFAULT_TEMPLATES.items():
        label = val.get("label", key)
        keyboard.append([types.InlineKeyboardButton(text=label, callback_data=f"select_tpl_{key}")])
    
    keyboard.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu")])
    
    await message.answer(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="Markdown")

@router.callback_query(F.data.startswith("select_tpl_"))
async def show_template_options(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    key = callback.data.split("select_tpl_")[1]
    
    tpl = await template_manager.get_template(key)
    label = tpl.get("label", key)
    
    preview_text = (
        f"📝 Шаблон: {label}\n\n"
        f"--- Текст ---\n{tpl['text']}\n-------------\n\n"
        f"Тип медиа: {tpl.get('media_type', 'none')}\n\n"
        "Что хотите изменить?"
    )
    
    keyboard = [
        [types.InlineKeyboardButton(text="✏️ Изменить текст", callback_data=f"edit_text_{key}")],
        [types.InlineKeyboardButton(text="🖼 Изменить/Добавить медиа", callback_data=f"edit_media_{key}")],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="content_list")]
    ]
    
    # If media exists, show it first? Or just show options.
    # It would be nice to send the actual template as preview.
    await template_manager.send_template(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        key=key,
        dynamic_text="\n\n👆 Это текущий вид сообщения."
    )

    await callback.message.answer(
        preview_text, 
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode=None
    )
    await callback.answer()

@router.callback_query(F.data == "content_list")
async def back_to_list(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await list_content(callback.message)
    await callback.message.delete()

@router.callback_query(F.data.startswith("edit_text_"))
async def edit_text_start(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split("edit_text_")[1]
    await state.update_data(template_key=key)
    await state.set_state(ContentState.waiting_for_new_text)
    
    await callback.message.edit_text(
        f"📝 **Редактирование текста для '{key}'**\n\n"
        "Отправьте новый текст сообщения.\n"
        "Медиа останется без изменений.",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_media_"))
async def edit_media_start(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split("edit_media_")[1]
    await state.update_data(template_key=key)
    await state.set_state(ContentState.waiting_for_new_media)
    
    await callback.message.edit_text(
        f"🖼 **Редактирование медиа для '{key}'**\n\n"
        "Отправьте фото, видео или GIF.\n"
        "Текст останется без изменений.",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_edit")
async def cancel_edit(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await list_content(callback.message)

@router.message(ContentState.waiting_for_new_text)
async def save_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("template_key")
    
    if not key:
        await message.answer("⚠️ Ошибка. Начните заново /content")
        await state.clear()
        return

    new_text = message.text or message.caption
    if not new_text:
         await message.answer("⚠️ Пришлите текст.")
         return

    # Get current template to preserve media
    current = await template_manager.get_template(key)
    media_type = current.get("media_type", "none")
    file_id = current.get("file_id")

    await template_manager.set_template(key, new_text, media_type, file_id)
    
    await message.answer("✅ Текст обновлен!")
    await state.clear()
    await list_content(message)

@router.message(ContentState.waiting_for_new_media)
async def save_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("template_key")
    
    if not key:
        await message.answer("⚠️ Ошибка. Начните заново /content")
        await state.clear()
        return

    media_type = "none"
    file_id = None

    if message.photo:
        media_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.animation:
        media_type = "animation"
        file_id = message.animation.file_id
    elif message.video:
        media_type = "video"
        file_id = message.video.file_id
    elif message.document:
        media_type = "document"
        file_id = message.document.file_id
    else:
        await message.answer("⚠️ Пришлите медиа (фото, видео, GIF) или нажмите Отмена.")
        return

    # Get current template to preserve text
    current = await template_manager.get_template(key)
    text = current.get("text", "")

    await template_manager.set_template(key, text, media_type, file_id)
    
    await message.answer(f"✅ Медиа обновлено (Тип: {media_type})!")
    await state.clear()
    await list_content(message)
