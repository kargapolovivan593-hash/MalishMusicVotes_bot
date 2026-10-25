
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ChannelPostHandler,
    CallbackQueryHandler,
    ContextTypes,
)

votes = {}

def keyboard(message_id):
    data = votes.setdefault(message_id, {})
    likes = sum(v == "like" for v in data.values())
    dislikes = sum(v == "dislike" for v in data.values())

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"❤️ {likes}", callback_data=f"like:{message_id}"
            ),
            InlineKeyboardButton(
                f"❌ {dislikes}", callback_data=f"dislike:{message_id}"
            ),
        ]
    ])

async def new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post = update.channel_post
    if not post:
        return

    msg = await context.bot.send_message(
        chat_id=post.chat_id,
        text="Оціни цей трек 👇",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❤️ 0", callback_data=f"like:{post.message_id}"),
            InlineKeyboardButton("❌ 0", callback_data=f"dislike:{post.message_id}"),
        ]]),
    )
    votes[msg.message_id] = {}

async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice, post_id = query.data.split(":")
    message_id = query.message.message_id
    user_id = query.from_user.id

    data = votes.setdefault(message_id, {})
    if data.get(user_id) == choice:
        del data[user_id]
    else:
        data[user_id] = choice

    await query.edit_message_reply_markup(
        reply_markup=keyboard(message_id)
    )

def main():
    token = os.environ["BOT_TOKEN"]
    app = Application.builder().token(token).build()
    app.add_handler(ChannelPostHandler(new_post))
    app.add_handler(CallbackQueryHandler(vote, pattern=r"^(like|dislike):"))
    app.run_polling()

if __name__ == "__main__":
    main()
  
