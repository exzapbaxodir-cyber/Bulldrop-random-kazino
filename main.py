from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8692829092:AAEzIExDusdb7PpDOy04bTspAFQnsS5v2l8"

ADMIN_ID = 8505635688  # o'z telegram id'ingni yoz

# ---------- PROMO LOAD ----------
def load_promos():
    promos = {}
    try:
        with open("promo.txt", "r") as f:
            for line in f:
                code, amount, used = line.strip().split(":")
                used_list = used.split(",") if used else []
                promos[code] = {
                    "amount": int(amount),
                    "used": used_list
                }
    except:
        pass
    return promos

# ---------- SAVE PROMO ----------
def save_promos(promos):
    with open("promo.txt", "w") as f:
        for code in promos:
            used_ids = ",".join(promos[code]["used"])
            f.write(f"{code}:{promos[code]['amount']}:{used_ids}\n")

# ---------- CREATE PROMO (ADMIN) ----------
async def createpromo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        code = context.args[0]
        amount = int(context.args[1])
    except:
        await update.message.reply_text("Format: /createpromo KOD 100")
        return

    promos = load_promos()
    promos[code] = {"amount": amount, "used": []}
    save_promos(promos)

    await update.message.reply_text(f"Promo yaratildi ✅\nKod: {code}\nCoin: {amount}")

# ---------- USE PROMO ----------
async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_code = context.args[0]
    except:
        await update.message.reply_text("Format: /promo KOD")
        return

    user_id = str(update.effective_user.id)
    promos = load_promos()

    if user_code not in promos:
        await update.message.reply_text("Promo topilmadi ❌")
        return

    if user_id in promos[user_code]["used"]:
        await update.message.reply_text("Siz bu promoni ishlatgansiz ❌")
        return

    amount = promos[user_code]["amount"]

    # BU YERDA FOYDALANUVCHIGA COIN QO'SHISH KODINI YOZASAN

    promos[user_code]["used"].append(user_id)
    save_promos(promos)

    await update.message.reply_text(f"Siz {amount} coin oldingiz 🎉")

# ---------- BOT START ----------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("createpromo", createpromo))
app.add_handler(CommandHandler("promo", promo))

app.run_polling()
