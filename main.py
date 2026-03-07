import asyncio
import logging
import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from src.utils.config import config
from src.handlers.users import start, payments, profile, support, mentorship
from src.handlers.admin import menu, broadcast, content, payments as admin_payments
from src.handlers.admins import access
from src.database.db import init_db
from src.database.db import async_session
from src.database.models import User, Payment, Message
from src.utils.scheduler import setup_scheduler
from src.utils.webapp_auth import validate_init_data, get_user_from_init_data
from sqlalchemy import select, func, update
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

async def handle_profile(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)

    user_id = int(tg_user.get("id"))

    async with async_session() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return web.json_response({"ok": False}, status=404)

        now = datetime.utcnow()
        is_subscribed = bool(user.has_active_subscription and (user.subscription_end is None or user.subscription_end > now))
        days_left = 0
        if user.subscription_end:
            delta = user.subscription_end - now
            days_left = max(0, delta.days)

        payments_stmt = select(Payment).where(
            Payment.user_id == user_id,
            Payment.status == "success",
            Payment.product_type.like("mentorship_%")
        )
        payments_result = await session.execute(payments_stmt)
        mentor_access = []
        for payment in payments_result.scalars().all():
            parts = payment.product_type.split("_")
            if len(parts) >= 2:
                mentor_access.append(parts[1])

        mentor_access = list({m for m in mentor_access})

    return web.json_response({
        "ok": True,
        "user": {
            "id": str(user_id),
            "nickname": user.full_name,
            "avatar": user.avatar,
            "is_admin": user_id in config.admins,
            "is_subscribed": is_subscribed,
            "days_left": days_left,
            "mentor_access": mentor_access
        }
    })

async def handle_profile_update(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)

    user_id = tg_user.get("id")
    nickname = payload.get("nickname")
    avatar = payload.get("avatar") # New field for avatar character/URL
    
    if not nickname:
        return web.json_response({"ok": False}, status=400)

    async with async_session() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user.full_name = nickname
            if avatar:
                user.avatar = avatar
            await session.commit()
            return web.json_response({"ok": True, "nickname": user.full_name, "avatar": user.avatar})

    return web.json_response({"ok": False}, status=404)

async def handle_payment_manual(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)

    user_id = tg_user.get("id")
    full_name = tg_user.get("first_name") or tg_user.get("username") or "User"
    username = tg_user.get("username")
    
    plan_id = payload.get("plan_id")
    method = payload.get("method")
    amount = payload.get("amount")
    currency = payload.get("currency")
    wallet = payload.get("wallet_address")

    if not all([plan_id, method, amount, currency]):
        return web.json_response({"ok": False}, status=400)

    # Validate amount to be a number
    try:
        amount = float(amount)
    except ValueError:
        return web.json_response({"ok": False}, status=400)

    # Create payment record
    async with async_session() as session:
        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            product_type=plan_id,
            status="manual_pending",
            crypto_pay_id=f"manual_{user_id}_{int(datetime.utcnow().timestamp())}"
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        payment_id = payment.id

    bot: Bot = request.app["bot"]
    admin_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Оплата пришла", callback_data=f"admin_pay_received_{payment_id}"),
            types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_pay_reject_{payment_id}")
        ]
    ])

    for admin_id in config.admins:
        try:
            await bot.send_message(
                admin_id,
                f"🔔 **ЗАЯВКА НА РУЧНУЮ ОПЛАТУ (WebApp API)**\n\n"
                f"👤 Пользователь: {full_name} (@{username or 'No username'})\n"
                f"🆔 ID: `{user_id}`\n"
                f"📦 Тариф: {plan_id}\n"
                f"💰 Сумма: {amount} {currency}\n"
                f"🕒 Дата: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                f"💳 Метод: {method.upper()}\n"
                f"👛 Кошелек: `{wallet}`\n"
                f"🆔 ID Заявки: `{payment_id}`",
                parse_mode="Markdown",
                reply_markup=admin_kb
            )
        except Exception as e:
            logging.error(f"Failed to notify admin {admin_id}: {e}")

    # Notify user about successful submission
    try:
        await bot.send_message(
            user_id,
            "✅ Ваша заявка на оплату принята!\nОжидайте подтверждения администратором."
        )
    except Exception as e:
        logging.error(f"Failed to notify user {user_id}: {e}")

    return web.json_response({"ok": True, "payment_id": payment_id})

async def handle_get_users(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)
        
    user_id = int(tg_user.get("id"))
    if user_id not in config.admins:
        return web.json_response({"ok": False}, status=403)

    action = payload.get("action")
    target_user_id = payload.get("target_user_id")

    if action == "toggle_subscription" and target_user_id:
        try:
            target_user_id = int(target_user_id)
            async with async_session() as session:
                stmt = select(User).where(User.telegram_id == target_user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                if user:
                    now = datetime.utcnow()
                    if user.has_active_subscription and (user.subscription_end is None or user.subscription_end > now):
                         # Cancel subscription
                         user.has_active_subscription = False
                         user.subscription_end = None
                         logging.info(f"Admin {user_id} cancelled subscription for {target_user_id}")
                    else:
                         # Grant subscription (1 month default)
                         user.has_active_subscription = True
                         user.subscription_end = now + timedelta(days=30)
                         logging.info(f"Admin {user_id} granted subscription for {target_user_id}")
                    await session.commit()
                    return web.json_response({"ok": True})
        except Exception as e:
             logging.error(f"Error toggling subscription: {e}")
             return web.json_response({"ok": False, "error": str(e)}, status=500)

    if action == "grant_mentor" and target_user_id:
        mentor_id = payload.get("mentor_id")
        if not mentor_id:
            return web.json_response({"ok": False, "error": "Mentor ID required"}, status=400)
            
        try:
            target_user_id = int(target_user_id)
            async with async_session() as session:
                # Add a record to payments as if it was a successful mentorship purchase
                payment = Payment(
                    user_id=target_user_id,
                    amount=0.0,
                    currency="ADMIN",
                    product_type=f"mentorship_{mentor_id}",
                    status="success",
                    crypto_pay_id=f"admin_grant_{target_user_id}_{mentor_id}_{int(datetime.utcnow().timestamp())}"
                )
                session.add(payment)
                await session.commit()
                logging.info(f"Admin {user_id} granted mentor {mentor_id} to {target_user_id}")
                return web.json_response({"ok": True})
        except Exception as e:
            logging.error(f"Error granting mentor access: {e}")
            return web.json_response({"ok": False, "error": str(e)}, status=500)

    async with async_session() as session:
        stmt = select(User).order_by(User.created_at.desc()).limit(100)
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        users_data = []
        now = datetime.utcnow()
        for u in users:
            is_subscribed = False
            if u.has_active_subscription:
                 if u.subscription_end is None:
                     is_subscribed = True
                 elif u.subscription_end > now:
                     is_subscribed = True
            
            users_data.append({
                "id": str(u.telegram_id),
                "name": u.full_name or u.username or "User",
                "role": "Admin" if u.telegram_id in config.admins else "User",
                "status": "Active",
                "isSubscribed": is_subscribed
            })

    return web.json_response({"ok": True, "users": users_data})

async def handle_get_payments(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)
        
    user_id = int(tg_user.get("id"))
    if user_id not in config.admins:
        return web.json_response({"ok": False}, status=403)

    action = payload.get("action")
    payment_id = payload.get("payment_id")

    if action == "approve" and payment_id:
        # Same logic as callback but for API
        async with async_session() as session:
            stmt = select(Payment).where(Payment.id == int(payment_id))
            result = await session.execute(stmt)
            payment = result.scalar_one_or_none()
            
            if payment and payment.status == "manual_pending":
                # For simplicity via API, let's just grant 30 days
                from src.services.payment_processing import process_successful_payment
                success = await process_successful_payment(request.app["bot"], session, payment)
                if success:
                    return web.json_response({"ok": True})
        return web.json_response({"ok": False}, status=400)

    async with async_session() as session:
        stmt = select(Payment).order_by(Payment.created_at.desc()).limit(100)
        result = await session.execute(stmt)
        payments = result.scalars().all()
        
        # Get users for names
        user_ids = [p.user_id for p in payments]
        user_stmt = select(User).where(User.telegram_id.in_(user_ids))
        user_result = await session.execute(user_stmt)
        users_map = {u.telegram_id: u.full_name or u.username or "User" for u in user_result.scalars().all()}
        
        payments_data = []
        for p in payments:
            payments_data.append({
                "id": str(p.id),
                "user": users_map.get(p.user_id, str(p.user_id)),
                "amount": f"{p.amount} {p.currency}",
                "date": p.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": p.status
            })

    return web.json_response({"ok": True, "payments": payments_data})

async def handle_get_user_payments(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)
        
    user_id = int(tg_user.get("id"))

    async with async_session() as session:
        stmt = select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at.desc())
        result = await session.execute(stmt)
        payments = result.scalars().all()
        
        payments_data = []
        for p in payments:
            payments_data.append({
                "id": p.id,
                "amount": f"{p.amount} {p.currency}",
                "product": p.product_type,
                "date": p.created_at.strftime("%d.%m.%Y %H:%M"),
                "status": p.status
            })

    return web.json_response({"ok": True, "payments": payments_data})

async def handle_chat_send(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)

    mentor_id = payload.get("mentor_id")
    text = payload.get("text")
    media_url = payload.get("media_url")
    if not mentor_id or (not text and not media_url):
        return web.json_response({"ok": False}, status=400)

    bot: Bot = request.app["bot"]
    full_name = tg_user.get("first_name") or tg_user.get("username") or "User"
    username = tg_user.get("username")
    user_id = tg_user.get("id")

    for admin_id in config.admins:
        try:
            msg_text = f"💬 **Новое сообщение из WebApp**\n\n" \
                       f"👤 Пользователь: {full_name} (@{username or 'No username'})\n" \
                       f"🆔 ID: `{user_id}`\n" \
                       f"👨‍🏫 Чат: {mentor_id}\n"
            if text:
                msg_text += f"✉️ Сообщение:\n{text}"
            
            if media_url:
                # If it's a local URL, we might need to send as photo
                if media_url.startswith("/uploads/"):
                    # For local testing, we send as text link, or could send file
                    # In production, this would be a real URL
                    full_media_url = f"{config.WEBAPP_API_URL}{media_url}"
                    await bot.send_photo(admin_id, photo=full_media_url, caption=msg_text, parse_mode="Markdown")
                else:
                    await bot.send_photo(admin_id, photo=media_url, caption=msg_text, parse_mode="Markdown")
            else:
                await bot.send_message(admin_id, msg_text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Failed to forward chat message to admin {admin_id}: {e}")

    # Save to DB
    async with async_session() as session:
        sender_type = "user"
        target_user_id = user_id
        
        reply_to = payload.get("target_id")
        if reply_to and str(user_id) in [str(admin) for admin in config.admins]:
            sender_type = "mentor"
            target_user_id = int(reply_to)

        msg = Message(
            user_id=target_user_id,
            mentor_id=mentor_id,
            text=text,
            media_url=media_url,
            sender=sender_type,
            created_at=datetime.utcnow()
        )
        session.add(msg)
        await session.commit()

    return web.json_response({"ok": True})

async def handle_upload(request: web.Request):
    # This endpoint handles image uploads for chats
    reader = await request.multipart()
    field = await reader.next()
    if field.name != 'file':
        return web.json_response({"ok": False, "error": "Invalid field name"}, status=400)
    
    filename = field.filename
    # Generate unique filename to avoid collisions
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, new_filename)
    
    size = 0
    with open(file_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)
            
    # Return the relative path to be used by the frontend
    return web.json_response({
        "ok": True, 
        "url": f"/uploads/{new_filename}"
    })

async def handle_get_messages(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)

    user_id = int(tg_user.get("id"))
    mentor_id = payload.get("mentor_id")
    target_id = payload.get("target_id") # For mentors to view specific user chat

    if not mentor_id:
        return web.json_response({"ok": False}, status=400)

    async with async_session() as session:
        query_user_id = user_id
        # If admin/mentor is requesting history for a specific user
        if target_id and user_id in config.admins:
            query_user_id = int(target_id)
            
        stmt = select(Message).where(
            Message.user_id == query_user_id,
            Message.mentor_id == mentor_id
        ).order_by(Message.created_at.asc())
        
        result = await session.execute(stmt)
        messages = result.scalars().all()
        
        # Mark as read if user is viewing
        if not target_id:
            # User is viewing their own chat with mentor_id
            update_stmt = update(Message).where(
                Message.user_id == user_id,
                Message.mentor_id == mentor_id,
                Message.sender == "mentor",
                Message.is_read == False
            ).values(is_read=True)
            await session.execute(update_stmt)
            await session.commit()
        elif user_id in config.admins:
            # Mentor is viewing specific user chat
            update_stmt = update(Message).where(
                Message.user_id == int(target_id),
                Message.mentor_id == mentor_id,
                Message.sender == "user",
                Message.is_read == False
            ).values(is_read=True)
            await session.execute(update_stmt)
            await session.commit()

        messages_data = [{
            "id": m.id,
            "text": m.text,
            "media_url": m.media_url,
            "sender": m.sender,
            "is_read": m.is_read,
            "time": m.created_at.strftime("%H:%M"),
            "date": m.created_at.strftime("%d.%m.%Y")
        } for m in messages]

    return web.json_response({"ok": True, "messages": messages_data})

async def handle_get_unread_counts(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)

    user_id = int(tg_user.get("id"))

    async with async_session() as session:
        # Count unread messages from mentors for this user
        stmt = select(Message.mentor_id, func.count(Message.id)).where(
            Message.user_id == user_id,
            Message.sender == "mentor",
            Message.is_read == False
        ).group_by(Message.mentor_id)
        
        result = await session.execute(stmt)
        counts = {mentor_id: count for mentor_id, count in result.all()}
        
        total_unread = sum(counts.values())

    return web.json_response({"ok": True, "counts": counts, "total": total_unread})

async def handle_get_stats(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)
        
    user_id = int(tg_user.get("id"))
    if user_id not in config.admins:
        return web.json_response({"ok": False}, status=403)

    async with async_session() as session:
        # Get statistics
        total_users_stmt = select(func.count(User.id))
        total_payments_stmt = select(func.count(Payment.id)).where(Payment.status == "success")
        total_revenue_stmt = select(func.sum(Payment.amount)).where(Payment.status == "success")
        
        total_users = (await session.execute(total_users_stmt)).scalar()
        total_payments = (await session.execute(total_payments_stmt)).scalar()
        total_revenue = (await session.execute(total_revenue_stmt)).scalar() or 0

        # Recent messages count
        unread_messages_stmt = select(func.count(Message.id)).where(Message.is_read == False, Message.sender == "user")
        unread_messages = (await session.execute(unread_messages_stmt)).scalar()

    return web.json_response({
        "ok": True,
        "stats": {
            "total_users": total_users,
            "total_payments": total_payments,
            "total_revenue": total_revenue,
            "unread_messages": unread_messages
        }
    })

async def handle_admin_broadcast(request: web.Request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)

    init_data = payload.get("init_data")
    if not init_data or not validate_init_data(init_data, config.BOT_TOKEN):
        return web.json_response({"ok": False}, status=401)

    tg_user = get_user_from_init_data(init_data)
    if not tg_user:
        return web.json_response({"ok": False}, status=400)
        
    user_id = int(tg_user.get("id"))
    if user_id not in config.admins:
        return web.json_response({"ok": False}, status=403)

    text = payload.get("text")
    if not text:
        return web.json_response({"ok": False, "error": "Message text required"}, status=400)

    bot: Bot = request.app["bot"]
    
    async with async_session() as session:
        stmt = select(User.telegram_id)
        result = await session.execute(stmt)
        user_ids = result.scalars().all()

    # Send messages in background to not block the API
    async def send_broadcast():
        count = 0
        for uid in user_ids:
            try:
                await bot.send_message(uid, text)
                count += 1
                await asyncio.sleep(0.05) # Rate limit protection
            except Exception as e:
                logging.error(f"Failed to broadcast to {uid}: {e}")
        logging.info(f"Broadcast completed. Sent to {count}/{len(user_ids)} users.")

    asyncio.create_task(send_broadcast())

    return web.json_response({"ok": True, "sent_to": len(user_ids)})

@web.middleware
async def cors_middleware(request: web.Request, handler):
    if request.method == "OPTIONS":
        return web.Response(headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Max-Age": "86400"
        })
    try:
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        return response
    except Exception as e:
        logging.error(f"Request failed: {e}")
        return web.json_response({"ok": False, "error": str(e)}, status=500, headers={
            "Access-Control-Allow-Origin": "*"
        })

async def handle_health(request: web.Request):
    return web.json_response({"status": "healthy", "uptime": "ok"})

async def handle_root(request: web.Request):
    return web.json_response({"message": "Gatee Bot API is running"})

async def start_webapp_api(bot: Bot):
    app = web.Application()
    app["bot"] = bot

    # CORS Middleware: Handle preflight and add headers to all responses
    @web.middleware
    async def cors_middleware(request, handler):
        if request.method == "OPTIONS":
            return web.Response(headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Access-Control-Max-Age": "86400"
            })
        
        try:
            response = await handler(request)
        except web.HTTPException as ex:
            ex.headers["Access-Control-Allow-Origin"] = "*"
            ex.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
            ex.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            return ex
        except Exception as e:
            logging.error(f"Request error: {e}", exc_info=True)
            return web.json_response({"ok": False, "error": str(e)}, status=500, headers={
                "Access-Control-Allow-Origin": "*"
            })

        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        return response

    # Logging Middleware
    @web.middleware
    async def logging_middleware(request, handler):
        logging.info(f"WEB REQUEST: {request.method} {request.path}")
        return await handler(request)

    app.middlewares.append(cors_middleware)
    app.middlewares.append(logging_middleware)

    # Generic dispatcher to handle multiple slashes and route correctly
    async def api_dispatcher(request):
        import re
        # Normalize path: remove any number of leading slashes and collapse internal ones
        # Example: ////api/profile -> /api/profile
        normalized_path = "/" + re.sub(r'/+', '/', request.path).lstrip('/')
        
        routes = {
            "/": handle_root,
            "/health": handle_health,
            "/api/profile": handle_profile,
            "/api/profile/update": handle_profile_update,
            "/api/payment/manual": handle_payment_manual,
            "/api/chat/send": handle_chat_send,
            "/api/chat/messages": handle_get_messages,
            "/api/chat/unread": handle_get_unread_counts,
            "/api/profile/payments": handle_get_user_payments,
            "/api/upload": handle_upload,
            "/api/admin/stats": handle_get_stats,
            "/api/admin/users": handle_get_users,
            "/api/admin/payments": handle_get_payments,
            "/api/admin/broadcast": handle_admin_broadcast
        }
        
        handler = routes.get(normalized_path)
        if handler:
            # Allow POST/GET for all API handlers, and handle OPTIONS via middleware
            if request.method in ["POST", "GET"]:
                return await handler(request)
            return web.json_response({"ok": False, "error": "Method Not Allowed"}, status=405)
            
        return web.json_response({"ok": False, "error": f"Not Found: {normalized_path}"}, status=404)

    # Catch all /api requests with any number of slashes
    app.router.add_route("*", "/{tail:.*}", api_dispatcher)
    
    # Static files for uploads
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    app.router.add_static("/uploads/", upload_dir)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, config.WEBAPP_API_HOST, config.WEBAPP_API_PORT)
    await site.start()
    logging.info(f"WebApp API started on {config.WEBAPP_API_HOST}:{config.WEBAPP_API_PORT}")
    return runner

async def main():
    # Initialize database
    logging.info("Initializing database...")
    await init_db()

    # Initialize bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Setup scheduler
    scheduler = setup_scheduler(bot)

    # Include routers
    dp.include_router(menu.router)
    dp.include_router(broadcast.router)
    dp.include_router(content.router)
    dp.include_router(admin_payments.router)
    dp.include_router(access.router)
    dp.include_router(start.router)
    dp.include_router(payments.router)
    dp.include_router(profile.router)
    dp.include_router(support.router)
    dp.include_router(mentorship.router)

    webapp_runner = await start_webapp_api(bot)

    # Start polling
    logging.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await webapp_runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
