import urllib.parse, requests
token=input("BOT_TOKEN: ").strip()
domain=input("Vercel domen (https://...): ").strip().rstrip("/")
url=f"{domain}/telegram/{urllib.parse.quote(token,safe='')}"
r=requests.post(f"https://api.telegram.org/bot{token}/setWebhook",json={"url":url},timeout=20)
print(r.status_code, r.text)
