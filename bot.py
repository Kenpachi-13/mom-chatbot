import os
import logging
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Загружаем ключи из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

ALLOWED_USERS = {856689872, 7238526055}  # твой и мамин ID

logging.basicConfig(level=logging.INFO)
client = OpenAI(api_key=OPENAI_KEY)


# Проверяем доступ
def allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update.effective_user.id):
        return
    await update.message.reply_text(
        "Бот запущен ✅\n\n"
        "Можешь писать вопросы или отправлять фото — я объясню, что на них."
    )

# Команда /id (для проверки)
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Твой Telegram ID: {update.effective_user.id}")

# Обработка текста
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not allowed(user_id):
        return

    user_message = update.message.text

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты дружелюбный помощник, объясняй просто и ясно."},
                {"role": "user", "content": user_message},
            ]
        )
        answer = completion.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"Ошибка при обращении к ChatGPT: {e}")

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not allowed(user_id):
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_path = "temp_image.jpg"
    await file.download_to_drive(image_path)

    await update.message.reply_text("Обрабатываю фото...")

    try:
        # Отправляем фото на анализ GPT-4o
        with open(image_path, "rb") as img:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты помощник, который объясняет, что изображено на фото."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Опиши это изображение максимально понятно."},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img.read().hex()}"}
                        ]
                    }
                ]
            )

        answer = completion.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"Ошибка при анализе фото: {e}")

# Основной запуск
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Бот запущен и готов к работе.")
    app.run_polling()

if __name__ == "__main__":
    main()
