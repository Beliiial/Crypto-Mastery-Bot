from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.utils.config import config
from src.services.template_manager import template_manager
import logging

router = Router()

class SupportState(StatesGroup):
    waiting_for_question = State()

class AdminSupportState(StatesGroup):
    waiting_for_reply = State()

@router.message(F.text == "❓ FAQ/Поддержка")
async def show_faq(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="👨‍💻 Связаться с админом", callback_data="contact_admin")]
    ])
    
    await template_manager.send_template(
        bot=message.bot,
        chat_id=message.chat.id,
        key="support_faq",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "contact_admin")
async def contact_admin(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📩 Пожалуйста, напишите ваш вопрос одним сообщением. Админ ответит вам в ближайшее время.")
    await state.set_state(SupportState.waiting_for_question)
    await callback.answer()

@router.message(SupportState.waiting_for_question)
async def process_support_question(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Forward question to all admins
    admin_notification = (
        "📩 **Новый вопрос от пользователя!**\n\n"
        f"👤 От: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"🆔 ID: `{message.from_user.id}`\n\n"
        f"📝 Вопрос: {message.text}"
    )
    
    for admin_id in config.admins:
        try:
            await message.bot.send_message(
                admin_id, 
                admin_notification, 
                parse_mode="Markdown",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="Ответить", callback_data=f"reply_{message.from_user.id}")]
                ])
            )
        except Exception as e:
            logging.error(f"Failed to notify admin {admin_id}: {e}")

    await message.answer("✅ Ваш вопрос отправлен админу. Ожидайте ответа!")

# Admin reply logic
@router.callback_query(F.data.startswith("reply_"))
async def admin_reply_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in config.admins:
        await callback.answer("⛔️ Только для админов!", show_alert=True)
        return

    user_id = callback.data.split("_")[1]
    await callback.message.answer(f"📝 Введите ответ для пользователя `{user_id}`:")
    await state.set_state(AdminSupportState.waiting_for_reply)
    await state.update_data(reply_to_user_id=user_id)
    await callback.answer()

@router.message(AdminSupportState.waiting_for_reply)
async def process_admin_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("reply_to_user_id")
    
    if not user_id:
        await message.answer("⚠️ Ошибка: неизвестный получатель.")
        await state.clear()
        return

    try:
        await message.bot.send_message(
            user_id,
            f"📩 **Ответ от поддержки:**\n\n{message.text}",
            parse_mode="Markdown"
        )
        await message.answer("✅ Ответ отправлен!")
    except Exception as e:
        await message.answer(f"⚠️ Не удалось отправить сообщение: {e}")
    
    await state.clear()
