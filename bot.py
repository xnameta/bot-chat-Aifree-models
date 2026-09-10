import os
import logging

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.constants import ChatAction

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

import database

from providers import openai_provider
from providers import cohere_provider
from providers import huggingface_provider
from providers import unsupported


load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


PROVIDERS = {
    "openai": {
        "name": "🟢 OpenAI",
        "handler": openai_provider.chat
    },

    "cohere": {
        "name": "🔵 Cohere",
        "handler": cohere_provider.chat
    },

    "huggingface": {
        "name": "🟡 Hugging Face",
        "handler": huggingface_provider.chat
    },

    "llama": {
        "name": "🦙 Meta Llama",
        "handler": unsupported.chat
    },

    "replicate": {
        "name": "🟣 Replicate",
        "handler": unsupported.chat
    },

    "stability": {
        "name": "🔴 Stability AI",
        "handler": unsupported.chat
    },

    "eleutherai": {
        "name": "⚪ EleutherAI",
        "handler": unsupported.chat
    }
}


def model_keyboard():

    buttons = []

    keys = list(PROVIDERS.keys())

    for i in range(0, len(keys), 2):

        row = []

        for key in keys[i:i + 2]:

            row.append(
                InlineKeyboardButton(
                    PROVIDERS[key]["name"],
                    callback_data=f"model:{key}"
                )
            )

        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(
            "🗑 Xóa lịch sử",
            callback_data="clear"
        )
    ])

    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    database.ensure_user(user_id)

    current = database.get_model(user_id)

    await update.message.reply_text(
        "🤖 AI MULTI-MODEL BOT\n\n"
        "Bạn có thể chat với nhiều AI provider.\n\n"
        f"🧠 Model hiện tại: {PROVIDERS[current]['name']}\n\n"
        "Chọn model bên dưới:",
        reply_markup=model_keyboard()
    )


async def models(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🧠 CHỌN AI\n\n"
        "Chọn provider bạn muốn sử dụng:",
        reply_markup=model_keyboard()
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    database.clear_history(user_id)

    await update.message.reply_text(
        "🗑 Đã xóa lịch sử trò chuyện."
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    database.ensure_user(user_id)

    data = query.data

    if data == "clear":

        database.clear_history(user_id)

        await query.edit_message_text(
            "🗑 Đã xóa lịch sử trò chuyện."
        )

        return

    if data.startswith("model:"):

        model = data.split(":", 1)[1]

        database.set_model(user_id, model)

        await query.edit_message_text(
            f"✅ Đã chuyển sang:\n\n"
            f"{PROVIDERS[model]['name']}\n\n"
            "Gửi tin nhắn để bắt đầu."
        )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    database.ensure_user(user_id)

    model = database.get_model(user_id)

    database.save_message(
        user_id,
        "user",
        update.message.text
    )

    history = database.get_history(
        user_id,
        limit=20
    )

    try:

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )

        handler = PROVIDERS[model]["handler"]

        response = await handler(history)

        if not response:
            response = "AI không trả về nội dung."

        database.save_message(
            user_id,
            "assistant",
            response
        )

        # Telegram giới hạn message khoảng 4096 ký tự
        for i in range(0, len(response), 4000):

            await update.message.reply_text(
                response[i:i + 4000]
            )

    except Exception as e:

        logging.exception("AI ERROR")

        await update.message.reply_text(
            "❌ Không thể gọi AI.\n\n"
            f"Provider: {PROVIDERS[model]['name']}\n"
            f"Lỗi: {str(e)}"
        )


def main():

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "Thiếu TELEGRAM_BOT_TOKEN trong .env"
        )

    database.init_db()

    app = (
        Application.builder()
        .token(token)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("models", models)
    )

    app.add_handler(
        CommandHandler("clear", clear)
    )

    app.add_handler(
        CallbackQueryHandler(button)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    logging.info("Bot đang chạy...")

    app.run_polling()


if __name__ == "__main__":
    main()