# -*- coding: utf-8 -*-
"""Stars & Premium demo bot: Vercel, 2 ENV, NO DATABASE.
Real payments, balances, fulfillment are intentionally disabled.
"""
import os
import logging
import telebot
from telebot import types
from flask import Flask, request, jsonify

BOT_TOKEN=os.getenv("BOT_TOKEN","").strip()
OWNER_RAW=os.getenv("OWNER_ID","").strip()
OWNER_ID=int(OWNER_RAW) if OWNER_RAW.isdigit() else 0
app=Flask(__name__)
bot=telebot.TeleBot(BOT_TOKEN, threaded=False) if ":" in BOT_TOKEN else None
logging.basicConfig(level=logging.INFO)
# Ephemeral cache only. Vercel may discard it after any request.
prices={"stars": 250, "premium_3": 60000, "premium_6": 110000, "premium_12": 210000}
def kb(rows):
    k=types.InlineKeyboardMarkup(row_width=2)
    for row in rows:
        k.row(*(types.InlineKeyboardButton(label,callback_data=key) for label,key in row))
    return k
def home(uid):
    rows=[
        [("⭐ Stars","stars"),("💎 Premium","premium")],
        [("💰 Hisobim","balance"),("📦 Buyurtmalarim","orders")],
        [("💳 Hisob to‘ldirish","topup"),("🎧 Yordam","help")],
    ]
    if uid==OWNER_ID: rows.append([("⚙️ Admin panel","admin")])
    return kb(rows)
def send(cid,txt,markup=None):
    bot.send_message(cid,txt,reply_markup=markup,parse_mode="HTML")
def process_message(msg):
    uid=msg.from_user.id
    if msg.text and msg.text.startswith("/start"):
        send(msg.chat.id,"⭐ <b>Stars & Premium</b>\n\nXush kelibsiz! Kerakli bo‘limni tanlang.",home(uid))
    elif msg.text and msg.text.startswith("/id"):
        send(msg.chat.id,f"Sizning Telegram ID: <code>{uid}</code>")
    elif msg.text and msg.text.startswith("/admin") and uid==OWNER_ID:
        send(msg.chat.id,"⚙️ Admin panel\n\nBazasiz rejim: narxlar vaqtinchalik, real savdo o‘chiq.",kb([[("📊 Holat","admin_status")],[("🏠 Bosh menyu","home")]]))
    else:
        send(msg.chat.id,"Bosh menyu:",home(uid))
def process_callback(call):
    uid=call.from_user.id
    cid=call.message.chat.id
    key=call.data or ""
    bot.answer_callback_query(call.id)
    back=kb([[("⬅️ Bosh menyu","home")]])
    if key=="home": send(cid,"🏠 Bosh menyu",home(uid))
    elif key=="stars":
        send(cid,f"⭐ <b>Telegram Stars</b>\n\n1 Stars: {prices['stars']:,} so‘m (namunaviy narx).\n\nReal xarid hozir o‘chirilgan.",back)
    elif key=="premium":
        send(cid,"💎 <b>Telegram Premium</b>\n\n"
            f"3 oy — {prices['premium_3']:,} so‘m\n"
            f"6 oy — {prices['premium_6']:,} so‘m\n"
            f"12 oy — {prices['premium_12']:,} so‘m\n\n"
            "Narxlar namunaviy. Real xarid hozir o‘chirilgan.",back)
    elif key=="balance": send(cid,"💰 Balans funksiyasi bazasiz rejimda mavjud emas.",back)
    elif key=="orders": send(cid,"📦 Buyurtmalar tarixi bazasiz rejimda saqlanmaydi.",back)
    elif key=="topup": send(cid,"💳 To‘lovlar xavfsizlik sababli o‘chirilgan. Bazasiz rejimda pul qabul qilinmaydi.",back)
    elif key=="help": send(cid,f"🎧 Yordam: bot administratori Telegram ID — <code>{OWNER_ID}</code>.",back)
    elif key in ("admin","admin_status") and uid==OWNER_ID:
        send(cid,"⚙️ <b>Admin panel</b>\n\n"
            "✅ Webhook va menyular ishlashi mumkin\n"
            "❌ Baza mavjud emas\n"
            "❌ To‘lov, balans va buyurtmalarni saqlash o‘chirilgan\n"
            "ℹ️ Narxlar kodda namunaviy berilgan.",back)
    else: send(cid,"Bosh menyu:",home(uid))
@app.get("/")
def index():
    return jsonify(ok=True,bot="Stars & Premium",mode="no_database_demo",configured=bool(bot and OWNER_ID),
                   real_payments_enabled=False,environment_variables=["BOT_TOKEN","OWNER_ID"])
@app.get("/health")
def health(): return index()
@app.route("/telegram",methods=["POST"])
def telegram():
    if not bot or not OWNER_ID: return jsonify(ok=False,error="BOT_TOKEN yoki OWNER_ID sozlanmagan"),503
    # Telegram secret path is derived from the token, so random callers cannot know it.
    return jsonify(ok=False,error="Use /telegram/<bot_token> webhook path"),404
@app.post("/telegram/<token>")
def telegram_secure(token):
    if not bot or not OWNER_ID or token!=BOT_TOKEN: return jsonify(ok=False),403
    try:
        update=telebot.types.Update.de_json(request.get_data(as_text=True))
        if update.message: process_message(update.message)
        if update.callback_query: process_callback(update.callback_query)
        return jsonify(ok=True)
    except Exception:
        app.logger.exception("Telegram update failed")
        return jsonify(ok=False),500
@app.get("/setup")
def setup():
    # Never expose token or allow arbitrary visitors to reconfigure the webhook.
    return jsonify(ok=False,message="Webhookni setup_webhook.py bilan o‘rnating."),403
