from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TOKEN, ADMIN_ID, DAILY_BONUS
from database import add_user, get_user, add_free, add_paid
from games import generate_ladder
from datetime import datetime

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)

    keyboard = [
        [InlineKeyboardButton("🎮 O'yinlar", callback_data="games")],
        [InlineKeyboardButton("💰 Balans", callback_data="balance")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus")]
    ]

    await update.message.reply_text(
        "Xush kelibsiz diqqat❗ bu bot o'zini omadiga ishonmaydigalar uchun 💯% random bot",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "balance":
        user = get_user(user_id)
        await query.edit_message_text(
            f"Free: {user[0]}\nPaid: {user[1]}"
        )

    if query.data == "games":
        keyboard = [
            [InlineKeyboardButton("🪜 Narvon (Free)", callback_data="ladder_free")],
            [InlineKeyboardButton("🪜 Narvon (Paid)", callback_data="ladder_paid")]
        ]
        await query.edit_message_text("O'yinni tanlang", reply_markup=InlineKeyboardMarkup(keyboard))

    if query.data == "ladder_free":
        row1, row2 = generate_ladder()
        text = "".join(row1) + "\n" + "".join(row2)
        await query.edit_message_text(f"FREE MODE\n{text}")

    if query.data == "ladder_paid":
        row1, row2 = generate_ladder()
        text = "".join(row1) + "\n" + "".join(row2)
        await query.edit_message_text(f"💎 PAID MODE 💎\n{text}")

    if query.data == "bonus":
        user = get_user(user_id)
        today = datetime.now().date()

        if user[2] == str(today):
            await query.edit_message_text("Bugun bonus olgansiz")
            return

        add_free(user_id, DAILY_BONUS)
        await query.edit_message_text(f"{DAILY_BONUS} coin berildi!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("Bot ishga tushdi")
app.run_polling()
