import requests

token = input('BOT_TOKEN (BotFather dagi YANGI token): ').strip()
domain = input('Vercel domen (https://...): ').strip().rstrip('/')
if not token or not domain.startswith('https://'):
    raise SystemExit('Token yoki https domen noto‘g‘ri')

url = f'{domain}/telegram/{token}'
response = requests.post(
    f'https://api.telegram.org/bot{token}/setWebhook',
    json={'url': url, 'allowed_updates': ['message', 'callback_query'], 'drop_pending_updates': True},
    timeout=20,
)
# Avoid printing token, which is embedded in the webhook URL.
if response.ok and response.json().get('ok'):
    print('OK: Webhook o‘rnatildi. Telegram botga /start yuboring.')
else:
    print('ERROR:', response.status_code, response.text[:300])
