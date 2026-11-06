# -*- coding: utf-8 -*-
"""Telegram Stars/Premium menu demonstration for Vercel (no database).

Environment variables: BOT_TOKEN, OWNER_ID.
Real payments, durable balances and fulfillment are NOT implemented.
"""
import logging
import os
import secrets

import telebot
from telebot import types
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
OWNER_ID_RAW = os.getenv('OWNER_ID', '').strip()
OWNER_ID = int(OWNER_ID_RAW) if OWNER_ID_RAW.isdecimal() else 0
bot = telebot.TeleBot(BOT_TOKEN, threaded=False) if BOT_TOKEN.count(':') == 1 else None
app = Flask(__name__)

# For illustration only. Values are not persisted across Vercel invocations.
prices = {'stars': 250, 'premium_3': 60000, 'premium_6': 110000, 'premium_12': 210000}


def keyboard(rows):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for row in rows:
        markup.row(*(types.InlineKeyboardButton(label, callback_data=key) for label, key in row))
    return markup


def home(uid):
    rows = [
        [('⭐ Stars', 'stars'), ('💎 Premium', 'premium')],
        [('💰 Hisobim', 'balance'), ('📦 Buyurtmalarim', 'orders')],
        [('💳 Hisob to‘ldirish', 'topup'), ('🎧 Yordam', 'help')],
    ]
    if uid == OWNER_ID:
        rows.append([('⚙️ Admin panel', 'admin')])
    return keyboard(rows)


def send(cid, text, markup=None):
    bot.send_message(cid, text, parse_mode='HTML', reply_markup=markup)


def process_message(msg):
    uid = msg.from_user.id
    command = (msg.text or '').split(maxsplit=1)[0].split('@', 1)[0].lower()
    if command in ('/start', '/cancel'):
        send(msg.chat.id, '⭐ <b>Stars &amp; Premium</b>\n\nXush kelibsiz! Kerakli bo‘limni tanlang.', home(uid))
    elif command == '/id':
        send(msg.chat.id, f'Sizning Telegram ID: <code>{uid}</code>')
    elif command == '/admin' and uid == OWNER_ID:
        send(msg.chat.id, '⚙️ Admin panel\n\nBazasiz demo rejimi.', keyboard([[('📊 Holat', 'admin_status')], [('🏠 Bosh menyu', 'home')]]))
    else:
        send(msg.chat.id, '🏠 Bosh menyu:', home(uid))


def process_callback(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    key = call.data or ''
    bot.answer_callback_query(call.id)
    back = keyboard([[('⬅️ Bosh menyu', 'home')]])
    if key == 'home':
        send(cid, '🏠 Bosh menyu', home(uid))
    elif key == 'stars':
        send(cid, f"⭐ <b>Telegram Stars</b>\n\n1 Stars: {prices['stars']:,} so‘m (namuna).\n\nReal xarid hozir o‘chirilgan.", back)
    elif key == 'premium':
        send(cid, '💎 <b>Telegram Premium</b>\n\n'
             f"3 oy — {prices['premium_3']:,} so‘m\n"
             f"6 oy — {prices['premium_6']:,} so‘m\n"
             f"12 oy — {prices['premium_12']:,} so‘m\n\n"
             'Narxlar namunaviy. Real xarid hozir o‘chirilgan.', back)
    elif key == 'balance':
        send(cid, '💰 Balans bazasiz rejimda saqlanmaydi.', back)
    elif key == 'orders':
        send(cid, '📦 Buyurtmalar tarixi bazasiz rejimda saqlanmaydi.', back)
    elif key == 'topup':
        send(cid, '💳 Bu demo versiyada haqiqiy to‘lov qabul qilinmaydi.', back)
    elif key == 'help':
        send(cid, f'🎧 Administrator Telegram ID: <code>{OWNER_ID}</code>', back)
    elif key in ('admin', 'admin_status') and uid == OWNER_ID:
        send(cid, '⚙️ <b>Admin panel</b>\n\n✅ Demo menyular\n❌ Ma’lumotlar bazasi\n❌ Real to‘lovlar\n❌ Doimiy balans va buyurtmalar', back)
    else:
        send(cid, '🏠 Bosh menyu:', home(uid))


@app.get('/')
@app.get('/health')
def health():
    return jsonify(ok=True, bot='Stars & Premium', configured=bool(bot and OWNER_ID), mode='no_database_demo', real_payments_enabled=False)


@app.post('/telegram/<path_token>')
def telegram_secure(path_token):
    if not bot or not OWNER_ID:
        logger.error('Missing BOT_TOKEN or OWNER_ID')
        return jsonify(ok=False, error='Configuration missing'), 503
    if not secrets.compare_digest(path_token, BOT_TOKEN):
        logger.warning('Webhook token mismatch')
        return jsonify(ok=False, error='Forbidden'), 403
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(ok=False, error='Expected Telegram JSON update'), 400
    try:
        update = types.Update.de_json(payload)
        if update.message:
            process_message(update.message)
        if update.callback_query:
            process_callback(update.callback_query)
        return jsonify(ok=True), 200
    except Exception:
        logger.exception('Telegram update failed')
        return jsonify(ok=False, error='Update processing failed'), 500


@app.post('/telegram')
def telegram_without_token():
    return jsonify(ok=False, error='Webhook should be /telegram/<BOT_TOKEN>'), 404
