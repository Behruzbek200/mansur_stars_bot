# Stars & Premium — FAQAT 2 ENV, BAZASIZ DEMO

Vercel Environment Variables:
- BOT_TOKEN
- OWNER_ID

Bu yangi, soddalashtirilgan **demo bot**. Oldingi botning barcha tijoriy funksiyalari ko‘chirilmagan.
Menyular: Stars, Premium, Hisobim, Buyurtmalarim, Hisob to‘ldirish, Yordam, Admin panel.
Baza yo‘q. Pul qabul qilish, avtomatik yetkazish, balans, buyurtmalarni saqlash **ishlamaydi**.
Narxlar faqat misol. Real sotuv uchun ishonchli doimiy baza va to‘lov integratsiyasi kerak.

1. ZIP ichidagi fayllarni GitHub repo rootiga yuklang.
2. Vercel → Settings → Environment Variables: BOT_TOKEN, OWNER_ID.
3. Neon yoki DATABASE_URL kerak emas. Oldingi database ENVs ishlatilmaydi.
4. Deploy qiling. Domen /health sahifasida configured:true bo‘lishi kerak.
5. Lokal kompyuterda `pip install requests`, keyin `python setup_webhook.py`.
6. Botga /start yuboring.

Muhim: Vercel webhook serverless; xabarlar faqat stateless ko‘rinishda ishlanadi.
