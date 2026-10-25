
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ChannelPostHandler,
    CallbackQueryHandler,
    ContextTypes,
)

votes = {}

def make_keyboard(post_id):
    data = votes.setdefault(post_id, {})
    likes = sum(v == "like" for v in data.values())
    dislikes = sum(v == "dislike" for v in data.values())

    return InlineKeyboardMarkup([[
        InlineKeyboardButton(f"❤️ {likes}", callback_data=f"like:{post_id}"),
        InlineKeyboardButton(f"❌ {dislikes}", callback_data=f"dislike:{post_id}"),
    ]])

async def new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post = update.channel_post
    if not post:
        return

    votes.setdefault(post.message_id, {})
    await context.bot.send_message(
        chat_id=post.chat_id,
        text="Оціни цей трек 👇",
        reply_markup=make_keyboard(post.message_id),
    )

async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice, post_id = query.data.split(":")
    post_id = int(post_id)
    data = votes.setdefault(post_id, {})
    user_id = query.from_user.id

    if data.get(user_id) == choice:
        del data[user_id]
    else:
        data[user_id] = choice

    await query.edit_message_reply_markup(
        reply_markup=make_keyboard(post_id)
    )

def main():
    token = os.environ["BOT_TOKEN"]
    external_url = os.environ["RENDER_EXTERNAL_URL"].rstrip("/")

    app = Application.builder().token(token).build()
    app.add_handler(ChannelPostHandler(new_post))
    app.add_handler(CallbackQueryHandler(vote, pattern=r"^(like|dislike):"))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        url_path=token,
        webhook_url=f"{external_url}/{token}",
    )

if __name__ == "__main__":
    main()
    
