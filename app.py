import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging setup (Render এর লগ দেখার জন্য জরুরি)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask('')

@app.route('/')
def home():
    # একদম ছোট রেসপন্স যাতে cron-job এ সমস্যা না হয়
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- কনফিগারেশন (Environment Variables থেকে নেওয়া ভালো) ---
BOT_TOKEN = "8641483673:AAGhYvt8z_mIOgzUQ4QyLWR15AvttFnAZwQ"
ADMIN_ID = 6665467890 

PO_VIP_LINK = "https://t.me/+v2r2SypmLiw4Yjk1"
QX_VIP_LINK = "https://t.me/+Iwm9dRAlyLI2YmI1"
PO_REF_LINK = "https://shorturl.at/lw0Tz"
QX_REF_LINK = "https://tinywebs.site/Lb38KA"

RESTART_TEXT = "\n\n🔄 পুনরায় শুরু করতে /start বাটনে ক্লিক করুন।"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("আমি VIP গ্রুপে জয়েন হতে চাই", callback_data='join_vip')]]
    context.user_data.clear() 
    await update.message.reply_text(
        "স্বাগতম! আমাদের ভিআইপি গ্রুপে জয়েন হওয়ার জন্য নিচের বাটনে ক্লিক করুন।" + RESTART_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    await query.answer()

    if data == 'join_vip':
        keyboard = [
            [InlineKeyboardButton("PocketOption VIP Group", callback_data='po_info')],
            [InlineKeyboardButton("Quotex VIP Group", callback_data='qx_info')],
            [InlineKeyboardButton("ইতিমধ্যে একাউন্ট করেছি", callback_data='already_account')]
        ]
        await query.edit_message_text("কোন ভিআইপি গ্রুপে জয়েন হতে চান?" + RESTART_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'po_info':
        await query.message.reply_text(f"পকেটঅপশনে একাউন্ট করতে এই লিংকে ক্লিক করুন: {PO_REF_LINK}\n\nএকাউন্ট করার পর আপনার ট্রেডার আইডিটি সাবমিট করুন।" + RESTART_TEXT)
    
    elif data == 'qx_info':
        await query.message.reply_text(f"কোটেক্স-এ একাউন্ট করতে এই লিংকে ক্লিক করুন: {QX_REF_LINK}\n\nএকাউন্ট করার পর আপনার ট্রেডার আইডিটি সাবমিট করুন।" + RESTART_TEXT)

    elif data == 'already_account':
        keyboard = [
            [InlineKeyboardButton("PocketOption ID জমা দিন", callback_data='submit_po')],
            [InlineKeyboardButton("Quotex ID জমা দিন", callback_data='submit_qx')]
        ]
        await query.edit_message_text("কোন সাইটের আইডি জমা দিতে চান?" + RESTART_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith('submit_'):
        platform = "PocketOption" if "po" in data else "Quotex"
        context.user_data['platform'] = platform
        await query.message.reply_text(f"আপনার {platform} ID টি এখানে টাইপ করে পাঠিয়ে দিন।" + RESTART_TEXT)

    elif data.startswith('approve_id_'):
        _, _, target_id, platform = data.split('_')
        keyboard = [[InlineKeyboardButton("আমি ডিপোজিট সম্পন্ন করেছি ✅", callback_data=f"done_dep_{platform}")]]
        await context.bot.send_message(
            chat_id=target_id,
            text=f"✅ আপনার {platform} আইডি ভেরিফাই করা হয়েছে!\n\nএখন ভিআইপি গ্রুপে জয়েন হতে কমপক্ষে $50 ডিপোজিট করুন এবং নিচের বাটনে ক্লিক করুন।" + RESTART_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.edit_message_text(f"ইউজার {target_id}-এর আইডি Approve করা হয়েছে।")

    elif data.startswith('reject_id_'):
        _, _, target_id, platform = data.split('_')
        await context.bot.send_message(chat_id=target_id, text=f"❌ দুঃখিত, আপনার {platform} আইডিটি সঠিক নয়। অনুগ্রহ করে সঠিক আইডি আবার সাবমিট করুন।" + RESTART_TEXT)
        await query.edit_message_text(f"ইউজার {target_id}-এর আইডি Reject করা হয়েছে।")

    elif data.startswith('done_dep_'):
        platform = data.split('_')[2]
        username = query.from_user.username or "N/A"
        admin_keyboard = [
            [InlineKeyboardButton("Approve Deposit ✅", callback_data=f"app_dep_{user_id}_{platform}")],
            [InlineKeyboardButton("Reject Deposit ❌", callback_data=f"rej_dep_{user_id}_{platform}")]
        ]
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 **ডিপোজিট নোটিশ!**\n\nইউজার: {user_id} (@{username})\nপ্ল্যাটফর্ম: {platform}\n\nচেক করে দেখুন।",
            reply_markup=InlineKeyboardMarkup(admin_keyboard)
        )
        await query.edit_message_text("আপনার ডিপোজিট রিকোয়েস্ট পাঠানো হয়েছে। চেক করার পর জানানো হবে।" + RESTART_TEXT)

    elif data.startswith('app_dep_'):
        _, _, target_id, platform = data.split('_')
        link = PO_VIP_LINK if platform == "PocketOption" else QX_VIP_LINK
        await context.bot.send_message(chat_id=target_id, text=f"🎊 অভিনন্দন! আপনার ডিপোজিট ভেরিফাই হয়েছে।\nলিংক: {link}" + RESTART_TEXT)
        await query.edit_message_text(f"ইউজার {target_id}-এর ডিপোজিট এপ্রুভ হয়েছে।")

    elif data.startswith('rej_dep_'):
        _, _, target_id, platform = data.split('_')
        await context.bot.send_message(chat_id=target_id, text="❌ ডিপোজিট সম্পন্ন হয়নি। দয়া করে আবার চেষ্টা করুন।" + RESTART_TEXT)
        await query.edit_message_text(f"ইউজার {target_id}-এর ডিপোজিট রিজেক্ট হয়েছে।")

async def handle_id_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'platform' in context.user_data:
        platform = context.user_data['platform']
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "N/A"
        submitted_id = update.message.text
        admin_keyboard = [[InlineKeyboardButton("Approve ID ✅", callback_data=f"approve_id_{user_id}_{platform}"), 
                           InlineKeyboardButton("Reject ID ❌", callback_data=f"reject_id_{user_id}_{platform}")]]
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 **নতুন আইডি!**\n\nপ্ল্যাটফর্ম: {platform}\nID: {submitted_id}\nইউজার: @{username}", reply_markup=InlineKeyboardMarkup(admin_keyboard))
        await update.message.reply_text(f"আপনার {platform} আইডিটি ভেরিফিকেশনের জন্য পাঠানো হয়েছে।" + RESTART_TEXT)
        context.user_data.pop('platform', None)

def main():
    # Flask Thread শুরু করা
    Thread(target=run_flask, daemon=True).start()
    
    # Telegram Bot শুরু করা
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_id_submission))
    
    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
