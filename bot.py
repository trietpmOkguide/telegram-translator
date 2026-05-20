import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from translator import translate_message

load_dotenv()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Hiển thị
# ──────────────────────────────────────────────

FLAG = {"vi": "🇻🇳", "ko": "🇰🇷", "en": "🇬🇧"}
LANG_NAME = {"vi": "Việt", "ko": "한국", "en": "English"}

LANG_ORDER = ["vi", "ko"]  # thứ tự ưu tiên hiển thị


def build_reply(detected_lang: str, translations: dict) -> str:
    """Tạo tin nhắn trả lời có format đẹp."""
    src_flag = FLAG.get(detected_lang, "🌐")
    lines = []

    for lang in LANG_ORDER:
        text = translations.get(lang, "").strip()
        if not text:
            continue
        dst_flag = FLAG.get(lang, "")
        lines.append(f"{src_flag}➜{dst_flag}  {text}")

    return "\n\n".join(lines)


# ──────────────────────────────────────────────
# Handler
# ──────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    # Bỏ qua tin nhắn của chính bot
    if message.from_user and message.from_user.is_bot:
        return

    text = message.text or message.caption
    if not text:
        return

    logger.info(
        "MSG from %s in chat %s: %.60s",
        message.from_user.username if message.from_user else "?",
        message.chat.id,
        text,
    )

    result = translate_message(text)
    if not result:
        return

    reply = build_reply(result["detected_lang"], result["translations"])
    if not reply:
        return

    try:
        await message.reply_text(reply, do_quote=True)
    except Exception as e:
        logger.error("Failed to send reply: %s", e)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN chưa được set trong file .env")

    app = Application.builder().token(token).build()

    # Lắng nghe tin nhắn text và media có caption (trừ command /xxx)
    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
            handle_message,
        )
    )

    logger.info("✅ Bot đang chạy... Nhấn Ctrl+C để dừng.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
