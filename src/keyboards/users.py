from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu(has_trial: bool = False):
    buttons = []
    if not has_trial:
        buttons.append([KeyboardButton(text="🎁 Получить пробный урок")])
    
    buttons.extend([
        [KeyboardButton(text="💎 Купить доступ")],
        [KeyboardButton(text="🎓 Личное обучение")],
        [KeyboardButton(text="👤 Личный кабинет")],
        [KeyboardButton(text="❓ FAQ/Поддержка")]
    ])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def mentorship_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍🏫 Ментор Gatee (1950 USDT)", callback_data="mentor_gatee")],
        [InlineKeyboardButton(text="👨‍🏫 Ментор Agwwee (3900 USDT)", callback_data="mentor_agwwee")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])

def buy_mentor_btn(mentor_code: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Заполнить анкету", callback_data=f"apply_mentor_{mentor_code}")],
        [InlineKeyboardButton(text="⭐️ Отзывы", callback_data=f"reviews_{mentor_code}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="mentorship_start")]
    ])

def reuse_application_btn(mentor_code: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 Отправить существующую", callback_data=f"reuse_app_{mentor_code}")],
        [InlineKeyboardButton(text="✏️ Исправить / Заполнить заново", callback_data=f"apply_mentor_{mentor_code}_new")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"mentor_{mentor_code}")]
    ])

def payment_options_btn(mentor_code: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить полностью", callback_data=f"pay_full_{mentor_code}")],
        [InlineKeyboardButton(text="📉 Рассрочка (50%)", callback_data=f"pay_half_{mentor_code}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"mentor_{mentor_code}")]
    ])

def buy_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 1 месяц - 150 USDT", callback_data="buy_1_month")],
        [InlineKeyboardButton(text="💎 3 месяца - 299 USDT", callback_data="buy_3_months")],
        [InlineKeyboardButton(text="💎 Навсегда - 599 USDT", callback_data="buy_forever")]
    ])

def profile_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Продлить подписку", callback_data="buy_access")],
        [InlineKeyboardButton(text="🤝 Пригласить друга", callback_data="referral_info")],
        [InlineKeyboardButton(text="💰 Вывести бонусы", callback_data="withdraw_bonuses")]
    ])