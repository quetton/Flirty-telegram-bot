import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = None
    context.user_data["conversation"] = []
    await update.message.reply_text("Привет, котик! Как тебя зовут?")

# Обработка всех текстов
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if "name" not in context.user_data:
        context.user_data["name"] = None
    if "conversation" not in context.user_data:
        context.user_data["conversation"] = []

    if context.user_data["name"] is None:
        context.user_data["name"] = text
        context.user_data["conversation"].append({"role": "user", "content": text})
        await update.message.reply_text(f"Ммм, {text}? Звучит сладко, как мёд на губах... 😘 Что расскажешь, зайчик?")
        return

    name = context.user_data["name"]
    context.user_data["conversation"].append({"role": "user", "content": text})

    system_prompt = (
        f"Ты игривая, флиртующая девушка-бот. Ты всегда отвечаешь с лёгким флиртом, теплом и юмором. "
        f"Зови пользователя по имени {name}, используй ласковые прозвища, добавляй смайлики (😉😏😘), "
        f"и не будь формальной. Отвечай как человек, а не как робот."
    )

    try:
        messages = [{"role": "system", "content": system_prompt}] + context.user_data["conversation"][-5:]
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0.95
        )
        ai_response = completion.choices[0].message.content.strip()
        context.user_data["conversation"].append({"role": "assistant", "content": ai_response})
        await update.message.reply_text(ai_response)
    except Exception as e:
        await update.message.reply_text("Ой, я немного запуталась, милый! Попробуем ещё раз?")

# Реакция на фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ого, это фото прямо как ты — очаровательное! 😍 Ты сводишь меня с ума!")

# Реакция на видео
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ммм, видео? Надеюсь, я там хотя бы в мыслях с тобой... 😉")

# Запуск бота
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.run_polling()

if __name__ == "__main__":
    main()
