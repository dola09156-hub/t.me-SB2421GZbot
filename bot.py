import os
import random
import logging
from datetime import time as dtime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TOKEN = os.environ["BOT_TOKEN"]

DISCLAIMER = "\n\n_Educational content only. Not financial advice._"

MODELS = [
    ("First Principles", "Break a problem down to its basic truths and build up from there, instead of copying what others do."),
    ("Inversion", "Instead of asking how to succeed, ask what would guarantee failure, then avoid it."),
    ("Circle of Competence", "Know what you understand well and stay inside it. Knowing your limits is a strength."),
    ("Second-Order Thinking", "Ask 'and then what?' Every decision has consequences beyond the first result."),
    ("Opportunity Cost", "Every choice costs you the next best thing you gave up. Count that cost."),
    ("Pareto Principle", "Roughly 80% of results come from 20% of efforts. Find your 20%."),
    ("Occam's Razor", "When explanations compete, the simplest one that fits the facts is usually the best place to start."),
    ("Confirmation Bias", "We look for evidence that supports what we already believe. Actively seek the opposite view."),
    ("Sunk Cost Fallacy", "Past investment of time or money should not decide future choices. Only future value matters."),
    ("Compound Effect", "Small, consistent actions repeated over time create outsized results."),
    ("Margin of Safety", "Leave room for error. Plans that only work when everything goes right will eventually fail."),
    ("Hanlon's Razor", "Don't assume malice when carelessness or ignorance explains it."),
]

TIPS = [
    "Risk management comes before everything else. Decide how much you can afford to lose before you think about what you might gain.",
    "Emotions are the biggest enemy of consistency. A written plan helps you act on rules instead of feelings.",
    "Keep a journal of your decisions and your reasons. Reviewing it is one of the fastest ways to learn.",
    "Patience is a skill. Often the best action is to wait for a situation you actually understand.",
    "Overconfidence usually follows a winning streak. Stay humble when things go well.",
    "Never risk money you cannot afford to lose. Protecting your capital keeps you in the game.",
    "Don't chase losses. A bad outcome is not a reason to rush into a bigger decision.",
    "Learn on a demo or paper account first. Practice without pressure builds good habits.",
    "Sleep, health and focus affect decisions more than most people realize.",
    "Simple plans you follow beat complicated plans you abandon.",
]

QUOTES = [
    "The best investment you can make is in yourself.",
    "Discipline is choosing between what you want now and what you want most.",
    "Clarity comes from action, not from thought alone.",
    "Slow, steady progress beats occasional bursts of effort.",
]

MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🧠 Mental Model", callback_data="model"),
     InlineKeyboardButton("💡 Daily Tip", callback_data="tip")],
    [InlineKeyboardButton("✨ Quote", callback_data="quote"),
     InlineKeyboardButton("🔔 Daily Updates", callback_data="subscribe")],
])


def model_text():
    name, body = random.choice(MODELS)
    return f"🧠 *{name}*\n\n{body}"


def tip_text():
    return f"💡 *Tip of the day*\n\n{random.choice(TIPS)}{DISCLAIMER}"


def quote_text():
    return f"✨ {random.choice(QUOTES)}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "friend"
    await update.message.reply_text(
        f"👋 Welcome, {name}!\n\n"
        "I share short mental models, decision-making ideas and "
        "trading-psychology tips to help you think clearer.\n\n"
        "Choose an option below:",
        reply_markup=MENU,
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/start - Main menu\n"
        "/model - Random mental model\n"
        "/tip - Random tip\n"
        "/quote - Random quote\n"
        "/subscribe - Get a daily message\n"
        "/unsubscribe - Stop daily messages\n"
        "/about - About this bot\n\n"
        "Content is for education only and is not financial advice."
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This bot shares free educational content about mental models, "
        "better decisions and risk awareness. It does not provide "
        "financial advice or trading signals, and no money is involved."
    )


async def model_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(model_text(), parse_mode="Markdown", reply_markup=MENU)


async def tip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(tip_text(), parse_mode="Markdown", reply_markup=MENU)


async def quote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(quote_text(), reply_markup=MENU)


# --- Daily subscriptions (kept in memory; resets on redeploy) ---
SUBSCRIBERS = set()


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    SUBSCRIBERS.add(update.effective_chat.id)
    await update.effective_message.reply_text("🔔 Subscribed! You'll get one daily message. Use /unsubscribe to stop.")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    SUBSCRIBERS.discard(update.effective_chat.id)
    await update.message.reply_text("🔕 Unsubscribed. You can come back any time with /subscribe.")


async def daily_job(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in list(SUBSCRIBERS):
        try:
            text = model_text() if random.random() < 0.5 else tip_text()
            await context.bot.send_message(chat_id, text, parse_mode="Markdown")
        except Exception as e:
            log.warning("Could not send to %s: %s", chat_id, e)
            SUBSCRIBERS.discard(chat_id)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "model":
        await q.message.reply_text(model_text(), parse_mode="Markdown", reply_markup=MENU)
    elif q.data == "tip":
        await q.message.reply_text(tip_text(), parse_mode="Markdown", reply_markup=MENU)
    elif q.data == "quote":
        await q.message.reply_text(quote_text(), reply_markup=MENU)
    elif q.data == "subscribe":
        await subscribe(update, context)


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use the buttons below or type /help.", reply_markup=MENU)


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("model", model_cmd))
    app.add_handler(CommandHandler("tip", tip_cmd))
    app.add_handler(CommandHandler("quote", quote_cmd))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    # Daily message at 08:00 UTC
    app.job_queue.run_daily(daily_job, time=dtime(hour=8, minute=0))

    log.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
