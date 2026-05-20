# Telegram Translator Bot — Setup Guide

## Bước 1: Tạo Telegram Bot

1. Mở Telegram → tìm **@BotFather**
2. Gõ `/newbot` → đặt tên → lấy **Bot Token** (dạng `1234567890:ABCdef...`)
3. Thêm bot vào group → vào Settings > Administrators → cấp quyền **Read Messages**

> **Quan trọng:** Vào @BotFather → `/mybots` → chọn bot → `Bot Settings` → `Group Privacy` → **Turn OFF**
> (Mặc định bot chỉ đọc được tin nhắn có `/` — tắt privacy mode để đọc tất cả)

---

## Bước 2: Cài đặt môi trường

```bash
cd ~/telegram-translator

# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Cài thư viện
pip install -r requirements.txt
```

---

## Bước 3: Cấu hình API keys

```bash
cp .env.example .env
```

Mở file `.env` và điền vào:

```
TELEGRAM_BOT_TOKEN=<token từ BotFather>
ANTHROPIC_API_KEY=<key từ console.anthropic.com>
```

---

## Bước 4: Chạy bot

```bash
source venv/bin/activate
python bot.py
```

Bot sẽ hiển thị: `✅ Bot đang chạy...`

---

## Cách bot hoạt động

| Tin nhắn trong group | Bot reply |
|---|---|
| 🇰🇷 Tiếng Hàn | 🇰🇷➜🇻🇳 Bản dịch tiếng Việt |
| 🇬🇧 Tiếng Anh | 🇬🇧➜🇻🇳 Bản dịch tiếng Việt |
| 🇻🇳 Tiếng Việt | 🇻🇳➜🇰🇷 + 🇻🇳➜🇬🇧 |
| Ngôn ngữ khác | Bỏ qua |

---

## Tùy chỉnh

### Đổi model AI (trong `translator.py` dòng 10)

```python
MODEL = "claude-haiku-4-5"    # Nhanh, rẻ — phù hợp dùng thường xuyên
MODEL = "claude-opus-4-6"     # Chất lượng cao nhất, đắt hơn ~5x
```

### Chỉ dịch Việt → Hàn (bỏ Anh)

Sửa `SYSTEM_PROMPT` trong `translator.py`:
```
- Tiếng Việt (vi) → chỉ Tiếng Hàn (ko)
```

---

## Deploy lên cloud (sau khi test local ổn)

### Railway (miễn phí $5/tháng credit)

```bash
# Cài Railway CLI
npm i -g @railway/cli

# Deploy
railway login
railway init
railway up
```

Thêm environment variables trong Railway dashboard (TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY).

### VPS (DigitalOcean, Vultr ~$4-6/tháng)

```bash
# Chạy nền với screen hoặc systemd
screen -S translator-bot
python bot.py
# Ctrl+A+D để detach
```

---

## Ước tính chi phí API

| Model | ~1000 tin nhắn/ngày | ~10,000 tin nhắn/ngày |
|---|---|---|
| claude-haiku-4-5 | ~$0.03/ngày | ~$0.30/ngày |
| claude-opus-4-6 | ~$0.15/ngày | ~$1.50/ngày |

> Khuyến nghị: dùng **haiku** cho group nhỏ, đã được set mặc định.
