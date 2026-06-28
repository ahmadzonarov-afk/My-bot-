import logging
import random
from datetime import datetime, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ─── НАСТРОЙКИ ────────────────────────────────────────────────
TOKEN = "8818407580:AAGbr8dbrfjCb06D5qMcpe55PNqgf0qBR6A"
MY_ID = 893933859  # число, без кавычек

# ─── ДАННЫЕ ───────────────────────────────────────────────────
HABITS = [
    ("🏋️", "Тренировка"),
    ("📚", "Читал книгу"),
    ("💰", "Пополнил инвест. счёт"),
    ("🗣️", "Практиковал речь"),
    ("📵", "Меньше соц. сетей"),
]

QUOTES = [
    "Дисциплина — это мост между целями и достижениями. — Джим Рон",
    "Маленькие шаги каждый день приводят к большим результатам.",
    "Богатство начинается с привычки откладывать. — Джордж Клейсон",
    "Тело достигает того, во что верит разум.",
    "Читай — и ты проживёшь тысячу жизней вместо одной.",
    "Инвестируй в себя. Это лучшее вложение, которое ты можешь сделать.",
    "Каждая тренировка — это победа над вчерашней версией себя.",
    "Не ищи мотивацию — строй дисциплину.",
    "Финансовая свобода начинается с первого перевода на счёт.",
    "Тот кто читает — управляет теми, кто смотрит телевизор.",
]

WORKOUT_TIPS = [
    "💪 Сегодня день тренировки! Разминка 5 минут, потом в бой.",
    "🔥 Помни: через день — это правило. Не нарушай его сегодня.",
    "⚡ 45 минут в зале сегодня = энергия на весь завтрашний день.",
    "🏆 Каждый подход делает тебя лучше. Вперёд!",
]

INVESTMENT_TIPS = [
    "📈 Регулярные вложения — ключ к капиталу. Даже маленькая сумма считается.",
    "💡 Правило: сначала заплати себе, потом остальным.",
    "🏠 Каждый перевод — кирпичик в стену твоей квартиры.",
    "📊 Не важна сумма — важна привычка инвестировать каждый месяц.",
]

# Хранилище данных (в памяти, сбрасывается при перезапуске)
user_data_store = {}

def get_today_key():
    return datetime.now().strftime("%Y-%m-%d")

def get_user_data():
    key = get_today_key()
    if key not in user_data_store:
        user_data_store[key] = {"habits": {h[1]: False for h in HABITS}}
    return user_data_store[key]

# ─── УТРЕННЕЕ СООБЩЕНИЕ ───────────────────────────────────────
async def morning_message(context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(QUOTES)
    now = datetime.now()
    day_name = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"][now.weekday()]

    text = (
        f"☀️ *Доброе утро!*\n"
        f"📅 {day_name}, {now.strftime('%d.%m.%Y')}\n\n"
        f"💬 _{quote}_\n\n"
        f"*План на сегодня:*\n"
        f"🏋️ Тренировка (если день тренировки)\n"
        f"📚 Читать книгу 20-30 минут\n"
        f"💰 Инвестиции (если 10-е или 25-е)\n"
        f"🗣️ Практика речи\n"
        f"📵 Меньше соц. сетей\n\n"
        f"Нажми /habits чтобы отмечать выполненное 👇"
    )
    await context.bot.send_message(chat_id=MY_ID, text=text, parse_mode="Markdown")

# ─── ВЕЧЕРНЕЕ СООБЩЕНИЕ ───────────────────────────────────────
async def evening_message(context: ContextTypes.DEFAULT_TYPE):
    data = get_user_data()
    habits = data["habits"]
    done = sum(1 for v in habits.values() if v)
    total = len(habits)
    percent = int(done / total * 100)

    if percent == 100:
        result = "🏆 Идеальный день! Ты выполнил всё!"
    elif percent >= 60:
        result = f"👍 Хороший день! {done} из {total} выполнено."
    else:
        result = f"😤 Можно лучше. Завтра исправим — {done} из {total}."

    lines = ""
    for emoji, name in HABITS:
        status = "✅" if habits[name] else "❌"
        lines += f"{status} {emoji} {name}\n"

    text = (
        f"🌙 *Вечерний итог дня*\n\n"
        f"{lines}\n"
        f"{result}\n\n"
        f"Ложись спать вовремя — завтра новый день 💪"
    )
    await context.bot.send_message(chat_id=MY_ID, text=text, parse_mode="Markdown")

# ─── КОМАНДЫ ──────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Привет! Я твой личный помощник.*\n\n"
        "Вот что я умею:\n\n"
        "📋 /habits — отметить привычки за сегодня\n"
        "💰 /invest — советы по инвестициям\n"
        "🏋️ /workout — совет по тренировке\n"
        "📚 /book — напоминание про книгу\n"
        "💬 /quote — случайная цитата\n"
        "📊 /stats — статистика за сегодня\n"
        "❓ /ask — задать мне любой вопрос\n\n"
        "Начнём? 🚀"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def habits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_user_data()
    habits = data["habits"]

    keyboard = []
    for emoji, name in HABITS:
        status = "✅" if habits[name] else "⬜"
        keyboard.append([InlineKeyboardButton(
            f"{status} {emoji} {name}",
            callback_data=f"habit_{name}"
        )])
    keyboard.append([InlineKeyboardButton("📊 Посмотреть итог", callback_data="show_stats")])

    await update.message.reply_text(
        "📋 *Привычки на сегодня*\nНажми чтобы отметить выполненное:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def habit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "show_stats":
        await stats_command_inline(query)
        return

    habit_name = query.data.replace("habit_", "")
    data = get_user_data()

    if habit_name in data["habits"]:
        data["habits"][habit_name] = not data["habits"][habit_name]

    habits = data["habits"]
    keyboard = []
    for emoji, name in HABITS:
        status = "✅" if habits[name] else "⬜"
        keyboard.append([InlineKeyboardButton(
            f"{status} {emoji} {name}",
            callback_data=f"habit_{name}"
        )])
    keyboard.append([InlineKeyboardButton("📊 Посмотреть итог", callback_data="show_stats")])

    done = sum(1 for v in habits.values() if v)
    total = len(habits)

    await query.edit_message_text(
        f"📋 *Привычки на сегодня* — {done}/{total} выполнено\nНажми чтобы отметить:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def stats_command_inline(query):
    data = get_user_data()
    habits = data["habits"]
    done = sum(1 for v in habits.values() if v)
    total = len(habits)
    percent = int(done / total * 100)

    lines = ""
    for emoji, name in HABITS:
        status = "✅" if habits[name] else "❌"
        lines += f"{status} {emoji} {name}\n"

    bar = "█" * (percent // 10) + "░" * (10 - percent // 10)

    text = (
        f"📊 *Статистика за сегодня*\n\n"
        f"{lines}\n"
        f"Прогресс: [{bar}] {percent}%\n"
        f"Выполнено: {done} из {total}"
    )
    await query.edit_message_text(text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_user_data()
    habits = data["habits"]
    done = sum(1 for v in habits.values() if v)
    total = len(habits)
    percent = int(done / total * 100)

    lines = ""
    for emoji, name in HABITS:
        status = "✅" if habits[name] else "❌"
        lines += f"{status} {emoji} {name}\n"

    bar = "█" * (percent // 10) + "░" * (10 - percent // 10)

    text = (
        f"📊 *Статистика за сегодня*\n\n"
        f"{lines}\n"
        f"Прогресс: [{bar}] {percent}%\n"
        f"Выполнено: {done} из {total}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def invest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tip = random.choice(INVESTMENT_TIPS)
    now = datetime.now()
    extra = ""
    if now.day in [10, 25]:
        extra = "\n\n🔔 *Сегодня день пополнения счёта! Не забудь сделать перевод.*"

    text = f"💰 *Инвестиции*\n\n{tip}{extra}"
    await update.message.reply_text(text, parse_mode="Markdown")

async def workout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tip = random.choice(WORKOUT_TIPS)
    text = f"🏋️ *Тренировка*\n\n{tip}"
    await update.message.reply_text(text, parse_mode="Markdown")

async def book_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 *Время читать!*\n\n"
        "Отложи телефон через 2 минуты и возьми книгу.\n"
        "Всего 20 минут в день = 12 книг в год.\n\n"
        "Прочитал? Отметь в /habits ✅"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(QUOTES)
    await update.message.reply_text(f"💬 _{quote}_", parse_mode="Markdown")

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❓ *Задай мне вопрос*\n\n"
        "Просто напиши своё сообщение — я отвечу.\n\n"
        "Например:\n"
        "• Как начать инвестировать?\n"
        "• Посоветуй книгу\n"
        "• Как улучшить речь?\n"
        "• Какие упражнения делать?"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()

    if any(w in user_text for w in ["инвест", "акци", "брокер", "деньги", "счёт", "вложить"]):
        tip = random.choice(INVESTMENT_TIPS)
        await update.message.reply_text(
            f"💰 *По теме инвестиций:*\n\n{tip}\n\nТакже: /invest",
            parse_mode="Markdown"
        )
    elif any(w in user_text for w in ["трениров", "качал", "зал", "упражнен", "спорт"]):
        tip = random.choice(WORKOUT_TIPS)
        await update.message.reply_text(
            f"🏋️ *По теме тренировок:*\n\n{tip}\n\nТакже: /workout",
            parse_mode="Markdown"
        )
    elif any(w in user_text for w in ["книг", "читать", "читал", "посоветуй книг"]):
        await update.message.reply_text(
            "📚 *Книги которые стоит прочитать:*\n\n"
            "💰 Финансы: «Богатый папа бедный папа» — Кийосаки\n"
            "🧠 Мышление: «Думай и богатей» — Хилл\n"
            "💪 Дисциплина: «Не давай мозгу лениться» — Амосов\n"
            "🗣️ Речь: «Говори красиво» — Ром\n"
            "⏰ Привычки: «Атомные привычки» — Клир",
            parse_mode="Markdown"
        )
    elif any(w in user_text for w in ["цитат", "мотивац", "вдохновен"]):
        quote = random.choice(QUOTES)
        await update.message.reply_text(f"💬 _{quote}_", parse_mode="Markdown")
    elif any(w in user_text for w in ["речь", "говорить", "общение", "коммуникац"]):
        await update.message.reply_text(
            "🗣️ *Как улучшить речь:*\n\n"
            "1. Читай вслух 10 минут в день\n"
            "2. Записывай себя на видео — слушай и исправляй\n"
            "3. Пересказывай прочитанное своими словами\n"
            "4. Учи 3 новых слова в день\n"
            "5. Смотри выступления TED на русском",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "🤖 Я понял твой вопрос! Вот команды которые помогут:\n\n"
            "/habits — привычки\n"
            "/invest — инвестиции\n"
            "/workout — тренировка\n"
            "/book — книга\n"
            "/quote — цитата\n"
            "/stats — статистика"
        )

# ─── ЗАПУСК ───────────────────────────────────────────────────
def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("habits", habits_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("invest", invest_command))
    app.add_handler(CommandHandler("workout", workout_command))
    app.add_handler(CommandHandler("book", book_command))
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("ask", ask_command))

    # Кнопки и сообщения
    app.add_handler(CallbackQueryHandler(habit_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Утреннее сообщение в 7:00
    app.job_queue.run_daily(morning_message, time=time(7, 0))

    # Вечернее сообщение в 21:00
    app.job_queue.run_daily(evening_message, time=time(21, 0))

    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
