import json
from aiogram import Bot, types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models import Setting
from src.database.db import async_session
import logging

DEFAULT_TEMPLATES = {
    "start_welcome": {
        "label": "Стартовое сообщение (/start)",
        "text": (
            "🚀 **Добро пожаловать в Gatee Bot!**\n\n"
            "Здесь мы зарабатываем на **арбитражных треугольниках**, **P2P-связках** и **CEX/DEX торговле**.\n\n"
            "Твоя цель — стабильный профит? Ты попал по адресу.\n\n"
            "👇 Выбери действие в меню:"
        ),
        "media_type": "none",
        "file_id": None
    },
    "trial_offer": {
        "label": "Предложение триала (кнопка в меню)",
        "text": (
            "🎁 **Забери бесплатный урок по Треугольникам!**\n\n"
            "Узнай, как находить спреды от 1% до 5% внутри биржи. Это база, с которой начинают наши ученики.\n\n"
            "Жми кнопку ниже 👇"
        ),
        "media_type": "none",
        "file_id": None
    },
    "trial_delivered": {
        "label": "Выдача триала (после нажатия)",
        "text": (
            "🎁 **Ваш пробный урок по CEX/DEX готов!**\n\n"
            "Мы подготовили для вас эксклюзивный материал: **'Основы поиска треугольников'**.\n\n"
            "📥 Скачать урок можно по ссылке ниже.\n\n"
            "🔥 **Понравилось?** Вступай в **Gatee Insider**, чтобы получать сигналы каждый день!"
        ),
        "media_type": "none",
        "file_id": None
    },
    "tarifs_list": {
        "label": "Список тарифов (Купить доступ)",
        "text": (
            "💎 **Приватный канал Gatee Insider**\n\n"
            "Что внутри:\n"
            "✅ Готовые связки CEX/DEX (спреды 1-3%)\n"
            "✅ Сигналы по внутрибиржевым треугольникам\n"
            "✅ Аналитика рынка 24/7\n\n"
            "Окупаемость подписки — от 1 сделки.\n\n"
            "Выберите тариф:"
        ),
        "media_type": "none",
        "file_id": None
    },
    "invoice_created": {
        "label": "Счет сформирован (после выбора тарифа)",
        "text": (
            "💳 **Счет на оплату сформирован!**\n\n"
            "Нажмите кнопку ниже, чтобы перейти к оплате в @CryptoBot. Доступ выдается автоматически.\n\n"
            "После оплаты вернитесь сюда."
        ),
        "media_type": "none",
        "file_id": None
    },
    "payment_success": {
        "label": "Успешная оплата (подписка)",
        "text": (
            "🎉 **Доступ открыт!**\n\n"
            "Добро пожаловать в команду Gatee Insider. Ссылка на канал ниже.\n\n"
            "Изучи закреп — там инструкция по первым сделкам."
        ),
        "media_type": "none",
        "file_id": None
    },
    "mentorship_main": {
        "label": "Менторство (главное меню)",
        "text": (
            "🎓 **Личное наставничество**\n\n"
            "Мы не просто даем сигналы, мы учим понимать рынок.\n\n"
            "**Программа:**\n"
            "🔹 Арбитраж (CEX/DEX)\n"
            "🔹 Поиск связок и треугольников\n"
            "🔹 Управление капиталом\n\n"
            "Результат: Выход на стабильный доход."
        ),
        "media_type": "none",
        "file_id": None
    },
    "profile_info": {
        "label": "Личный кабинет",
        "text": (
            "👤 **Личный кабинет**\n\n"
            "Твоя статистика и реферальная программа.\n\n"
            "Приглашай друзей и получай % с их оплат!"
        ),
        "media_type": "none",
        "file_id": None
    },
    "support_faq": {
        "label": "FAQ / Поддержка",
        "text": (
            "❓ **Часто задаваемые вопросы**\n\n"
            "1️⃣ **Что такое треугольник?**\n"
            "Это цепочка обменов внутри одной биржи с профитом на выходе.\n\n"
            "2️⃣ **Нужен ли большой депозит?**\n"
            "Можно начать со 100 USDT.\n\n"
            "3️⃣ **Как оплатить?**\n"
            "Нажмите 'Купить доступ' -> CryptoBot."
        ),
        "media_type": "none",
        "file_id": None
    },
    "reminder_trial_24h": {
        "label": "Напоминание (24ч после триала)",
        "text": (
            "👋 **Как успехи с треугольниками?**\n\n"
            "Прошли сутки. Если тема зашла — не теряй время.\n\n"
            "В **Gatee Insider** мы даем готовые сетапы каждый день.\n\n"
            "💎 **Жми 'Купить доступ' и залетай в рынок!**"
        ),
        "media_type": "none",
        "file_id": None
    },
    "reminder_sub_3d": {
        "label": "Напоминание (3 дня до конца подписки)",
        "text": (
            "⏳ **Осталось 3 дня!**\n\n"
            "Твоя подписка скоро истечет. Не теряй доступ к сигналам.\n\n"
            "Продли сейчас в Личном кабинете."
        ),
        "media_type": "none",
        "file_id": None
    },
    "reminder_sub_1d": {
        "label": "Напоминание (1 день до конца подписки)",
        "text": (
            "⚠️ **ЗАВТРА финиш!**\n\n"
            "Подписка истекает. Продли, чтобы не пропустить завтрашние связки!"
        ),
        "media_type": "none",
        "file_id": None
    },
    "mentorship_success": {
        "label": "Успешная оплата (менторство)",
        "text": (
            "🎉 **Оплата обучения подтверждена!**\n\n"
            "Администратор уже получил уведомление и свяжется с вами в ближайшее время для назначения первого созвона.\n\n"
            "Если есть вопросы — пишите в поддержку."
        ),
        "media_type": "none",
        "file_id": None
    },
    "referral_reward": {
        "label": "Уведомление о реферальном бонусе",
        "text": (
            "💰 **Вам начислен бонус!**\n\n"
            "Ваш друг оплатил доступ. 10% от суммы зачислено на ваш баланс.\n\n"
            "Продолжайте приглашать и зарабатывать!"
        ),
        "media_type": "none",
        "file_id": None
    }
}

class TemplateManager:
    async def get_template(self, key: str) -> dict:
        async with async_session() as session:
            stmt = select(Setting).where(Setting.key == f"tpl:{key}")
            result = await session.execute(stmt)
            setting = result.scalar_one_or_none()
            
            # Default structure
            default = DEFAULT_TEMPLATES.get(key, {"label": key, "text": "Текст не задан.", "media_type": "none", "file_id": None})
            
            if setting:
                try:
                    data = json.loads(setting.value)
                    # Merge with default label if missing in DB (legacy)
                    if "label" not in data:
                        data["label"] = default.get("label", key)
                    return data
                except:
                    pass
            
            return default

    async def set_template(self, key: str, text: str, media_type: str = "none", file_id: str = None):
        # We should preserve the label
        current = await self.get_template(key)
        label = current.get("label", key)

        async with async_session() as session:
            value = json.dumps({
                "label": label,
                "text": text,
                "media_type": media_type,
                "file_id": file_id
            }, ensure_ascii=False)
            
            stmt = select(Setting).where(Setting.key == f"tpl:{key}")
            result = await session.execute(stmt)
            setting = result.scalar_one_or_none()
            
            if setting:
                setting.value = value
            else:
                setting = Setting(key=f"tpl:{key}", value=value)
                session.add(setting)
            
            await session.commit()

    async def send_template(self, bot: Bot, chat_id: int, key: str, **kwargs):
        tpl = await self.get_template(key)
        text = tpl.get("text", "")
        media_type = tpl.get("media_type", "none")
        file_id = tpl.get("file_id")
        
        dynamic_text = kwargs.pop('dynamic_text', "")
        if dynamic_text:
            text += f"\n{dynamic_text}"

        reply_markup = kwargs.get("reply_markup")
        parse_mode = kwargs.get("parse_mode", "Markdown")

        try:
            if media_type == "photo" and file_id:
                await bot.send_photo(chat_id, file_id, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
            elif media_type == "animation" and file_id:
                await bot.send_animation(chat_id, file_id, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
            elif media_type == "video" and file_id:
                await bot.send_video(chat_id, file_id, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
            elif media_type == "document" and file_id:
                await bot.send_document(chat_id, file_id, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                await bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
            return True
        except Exception as e:
            logging.error(f"Failed to send template {key} to {chat_id}: {e}")
            return False
            
    # Helper for editing messages (updating text/media)
    async def edit_message_template(self, message: types.Message, key: str, **kwargs):
        tpl = await self.get_template(key)
        text = tpl.get("text", "")
        reply_markup = kwargs.get("reply_markup")
        parse_mode = kwargs.get("parse_mode", "Markdown")
        
        try:
            if not message.photo and not message.video and not message.animation and tpl['media_type'] == 'none':
                 await message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                await message.delete()
                await self.send_template(message.bot, message.chat.id, key, **kwargs)
        except Exception as e:
            logging.error(f"Failed to edit template {key}: {e}")
            await self.send_template(message.bot, message.chat.id, key, **kwargs)

template_manager = TemplateManager()
