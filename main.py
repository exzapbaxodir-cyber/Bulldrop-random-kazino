# main.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
import random
import json
import os

# ---------- CONFIG ----------
TOKEN = "8692829092:AAEzIExDusdb7PpDOy04bTspAFQnsS5v2l8"
ADMIN_ID = 8505635688
DAILY_FREE_COIN = 5
PAID_COIN_AMOUNT = 50

# ---------- DATABASE ----------
USERS_FILE = "users.json"
PROMO_FILE = "promo.txt"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# Load / Save users
def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# ---------- PROMO ----------
def load_promos():
    promos = {}
    if os.path.exists(PROMO_FILE):
        with open(PROMO_FILE, "r") as f:
            for line in f:
                code, amount, used = line.strip().split(":")
                used_list = used.split(",") if used else []
                promos[code] = {"amount": int(amount), "used": used_list}
    return promos

def save_promos(promos):
    with open(PROMO_FILE, "w") as f:
        for code, info in promos.items():
            used_ids = ",".join(info["used"])
            f.write(f"{code}:{info['amount']}:{used_ids}\n")

def use_promo(user_id, code):
    user_id = str(user_id)
    promos = load_promos()
    if code not in promos:
        return 0, "NOT_FOUND"
    if user_id in promos[code]["used"]:
        return 0, "USED"
    amount = promos[code]["amount"]
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"free":0,"paid":0,"last_bonus":""}
    users[str(user_id)]["free"] += amount
    save_users(users)
    promos[code]["used"].append(user_id)
    save_promos(promos)
    return amount, "OK"

def create_promo_admin(code, amount):
    promos = load_promos()
    promos[code] = {"amount": amount, "used": []}
    save_promos(promos)

# ---------- USERS ----------
def add_user(user_id):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"free":0,"paid":0,"last_bonus":""}
        save_users(users)

def get_user(user_id):
    users = load_users()
    return users.get(str(user_id), {"free":0,"paid":0,"last_bonus":""})

def add_coin(user_id, coin_type, amount):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"free":0,"paid":0,"last_bonus":""}
    users[str(user_id)][coin_type] += amount
    save_users(users)

def take_coin(user_id, coin_type, amount):
    users = load_users()
    users[str(user_id)][coin_type] -= amount
    save_users(users)

# ---------- GAMES ----------
def generate_ladder():
    row1 = ["⬜"]*10
    row2 = ["⬜"]*10
    bombs1 = random.sample(range(10),3)
    bombs2 = random.sample(range(10),3)
    for b in bombs1: row1[b]="💣"
    for b in bombs2: row2[b]="💣"
    return row1,row2

def sapyor_board():
    board = [["⬜"]*5 for _ in range(5)]
    bombs = random.sample(range(25),5)
    for b in bombs:
        x,y = divmod(b,5)
        board[x][y]="💣"
    return board

def bulldrop_wheel():
    colors = ["🟦"]*12 + ["🟩"]*7 + ["🟥"]*7 + ["🟪"]
    return random.choice(colors)

def minora():
    board = []
    for i in range(8):
        board.append(random.choice(["➡️","⬅️"]))
    return board

def krash():
    return round(random.uniform(1.0,10.0),2)

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    keyboard = [
        [InlineKeyboardButton("🎮 O'yinlar", callback_data="games")],
        [InlineKeyboardButton("💰 Balans", callback_data="balance")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus")],
        [InlineKeyboardButton("🎟 Promo", callback_data="promo")]
    ]
    await update.message.reply_text("Xush kelibsiz! 🔥", reply_markup=InlineKeyboardMarkup(keyboard))

# ---------- BUTTON HANDLER ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    paid = user["paid"]>0
    if query.data=="balance":
        await query.edit_message_text(f"💰 Free: {user['free']}\n💎 Paid: {user['paid']}")
    elif query.data=="bonus":
        today = str(datetime.now().date())
        if user["last_bonus"]==today:
            await query.edit_message_text("Bugun bonus olgansiz ❌")
            return
        add_coin(user_id,"free",DAILY_FREE_COIN)
        users = load_users()
        users[str(user_id)]["last_bonus"]=today
        save_users(users)
        await query.edit_message_text(f"{DAILY_FREE_COIN} free coin berildi! ✅")
    elif query.data=="games":
        keyboard = [
            [InlineKeyboardButton("🪜 Narvon", callback_data="ladder")],
            [InlineKeyboardButton("💣 Sapyor", callback_data="sapyor")],
            [InlineKeyboardButton("🎡 Bulldrop", callback_data="bulldrop")],
            [InlineKeyboardButton("🏰 Minora", callback_data="minora")],
            [InlineKeyboardButton("💹 Krash", callback_data="krash")]
        ]
        await query.edit_message_text("O'yin tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data=="ladder":
        if user["free"]<1:
            await query.edit_message_text("Coin yetarli emas ❌")
            return
        if paid: take_coin(user_id,"paid",0)
        else: take_coin(user_id,"free",1)
        r1,r2 = generate_ladder()
        text = " ".join(r1)+"\n"+" ".join(r2)
        await query.edit_message_text(("💎 PREMIUM MODE\n"+text) if paid else text)
    elif query.data=="sapyor":
        if user["free"]<1:
            await query.edit_message_text("Coin yetarli emas ❌")
            return
        if paid: take_coin(user_id,"paid",0)
        else: take_coin(user_id,"free",1)
        board = sapyor_board()
        text = "\n".join([" ".join(r) for r in board])
        await query.edit_message_text(("💎 PREMIUM MODE\n"+text) if paid else text)
    elif query.data=="bulldrop":
        if user["free"]<1:
            await query.edit_message_text("Coin yetarli emas ❌")
            return
        if paid: take_coin(user_id,"paid",0)
        else: take_coin(user_id,"free",1)
        color = bulldrop_wheel()
        await query.edit_message_text(("💎 PREMIUM MODE\n"+color) if paid else color)
    elif query.data=="minora":
        if user["free"]<1:
            await query.edit_message_text("Coin yetarli emas ❌")
            return
        if paid: take_coin(user_id,"paid",0)
        else: take_coin(user_id,"free",1)
        board = minora()
        text = " ".join(board)
        await query.edit_message_text(("💎 PREMIUM MODE\n"+text) if paid else text)
    elif query.data=="krash":
        if user["free"]<1:
            await query.edit_message_text("Coin yetarli emas ❌")
            return
        if paid: take_coin(user_id,"paid",0)
        else: take_coin(user_id,"free",1)
        mult = krash()
        await query.edit_message_text(("💎 PREMIUM MODE\n"+str(mult)) if paid else str(mult))
    elif query.data=="promo":
        await query.edit_message_text("Promo ishlatish: /promo KOD\nAdmin yaratish: /createpromo KOD COIN")

# ---------- COMMANDS ----------
async def promo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        code = context.args[0]
    except:
        await update.message.reply_text("Format: /promo KOD")
        return
    amount,status = use_promo(update.effective_user.id, code)
    if status=="NOT_FOUND":
        await update.message.reply_text("Promo topilmadi ❌")
    elif status=="USED":
        await update.message.reply_text("Siz bu promoni ishlatgansiz ❌")
    else:
        await update.message.reply_text(f"{amount} coin oldingiz 🎉")

async def createpromo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID:
        await update.message.reply_text("Admin emassiz ❌")
        return
    try:
        code = context.args[0]
        amount = int(context.args[1])
    except:
        await update.message.reply_text("Format: /createpromo KOD COIN")
        return
    create_promo_admin(code, amount)
    await update.message.reply_text(f"Promo yaratildi ✅\nKod: {code}\nCoin: {amount}")

# ---------- RUN ----------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("promo", promo_cmd))
app.add_handler(CommandHandler("createpromo", createpromo_cmd))

print("Bot ishga tushdi ✅")
app.run_polling()
