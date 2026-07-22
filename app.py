import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Flask App for Health Check (Koyeb এর জন্য প্রয়োজন)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=os.getenv("PORT", 8080))

# --- কনফিগারেশন (Environment Variables থেকে আসবে) ---
BOT_TOKEN = os.getenv("8641483673:AAEpclw3nauQWD1Swm2-3stf0lGq5A358VM")
ADMIN_ID = int(os.getenv("6665467890"))

# এখানে আপনার গ্রুপের লিংকগুলো দিন
PO_VIP_LINK = "https://t.me/+v2r2SypmLiw4Yjk1"
QX_VIP_LINK = "https://t.me/+Iwm9dRAlyLI2YmI1"

# রেফারেল লিংক
PO_REF_LINK = "https://shorturl.at/lw0Tz"
QX_REF_LINK = "https://tinywebs.site/Lb38KA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("আমি VIP গ্রুপে জয়েন হতে চাই", callback_data='join_vip')]]
    await update.message.reply_text(
        "স্বাগতম! আমাদের ভিআইপি গ্রুপে জয়েন হওয়ার জন্য নিচের বাটনে ক্লিক করুন।",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'join_vip':
        keyboard = [
            [InlineKeyboardButton("PocketOption VIP Group", callback_data='po_info')],
            [InlineKeyboardButton("Quotex VIP Group", callback_data='qx_info')],
            [InlineKeyboardButton("ইতিমধ্যে একাউন্ট করেছি", callback_data='already_account')]
        ]
        await query.edit_message_text("কোন ভিআইপি গ্রুপে জয়েন হতে চান?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'po_info':
        await query.message.reply_text(f"পকেটঅপশনে একাউন্ট করতে এই লিংকে ক্লিক করুন: {PO_REF_LINK}\n\nএকাউন্ট করার পর আপনার ট্রেডার আইডিটি সাবমিট করুন।")
    
    elif query.data == 'qx_info':
        await query.message.reply_text(f"কোটেক্স-এ একাউন্ট করতে এই লিংকে ক্লিক করুন: {QX_REF_LINK}\n\nএকাউন্ট করার পর আপনার ট্রেডার আইডিটি সাবমিট করুন।")

    elif query.data == 'already_account':
        keyboard = [
            [InlineKeyboardButton("PocketOption ID জমা দিন", callback_data='submit_po')],
            [InlineKeyboardButton("Quotex ID জমা দিন", callback_data='submit_qx')]
        ]
        await query.edit_message_text("কোন সাইটের আইডি জমা দিতে চান?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith('submit_'):
        platform = "PocketOption" if "po" in query.data else "Quotex"
        # ইউজারের পছন্দের প্ল্যাটফর্ম সেভ করে রাখা হচ্ছে
        context.user_data['platform'] = platform
        await query.message.reply_text(f"আপনার {platform} ID টি এখানে টাইপ করে পাঠিয়ে দিন।")

    # এডমিন যখন Approve বাটনে ক্লিক করবে
    elif query.data.startswith('approve_'):
        # তথ্য সংগ্রহ: approve_USERID_PLATFORM
        _, target_user_id, platform = query.data.split('_')
        
        if platform == "PocketOption":
            link = PO_VIP_LINK
        else:
            link = QX_VIP_LINK
            
        try:
            await context.bot.send_message(
                chat_id=target_user_id, 
                text=f"✅ অভিনন্দন! আপনার {platform} আইডিটি ভেরিফাই করা হয়েছে।\n\nনিচের লিংকে ক্লিক করে ভিআইপি গ্রুপে জয়েন করুন:\n{link}"
            )
            await query.edit_message_text(f"ইউজার {target_user_id}-কে {platform} গ্রুপের লিংক পাঠানো হয়েছে।")
        except Exception as e:
            await query.edit_message_text(f"Error: {e}")

async def handle_id_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'platform' in context.user_data:
        platform = context.user_data['platform']
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "N/A"
        submitted_id = update.message.text

        # এডমিনের কাছে মেসেজ পাঠানো (প্ল্যাটফর্ম অনুযায়ী আলাদা বাটন)
        admin_keyboard = [[InlineKeyboardButton(f"Approve {platform} ✅", callback_data=f"approve_{user_id}_{platform}")]]
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(f"📩 নতুন আইডি জমা পড়েছে!\n\n"
                  f"প্ল্যাটফর্ম: {platform}\n"
                  f"ট্রেডার আইডি: {submitted_id}\n"
                  f"টেলিগ্রাম ইউজার: @{username}\n"
                  f"ইউজার আইডি: {user_id}"),
            reply_markup=InlineKeyboardMarkup(admin_keyboard)
        )
        
        await update.message.reply_text(f"আপনার {platform} আইডিটি এডমিনের কাছে পাঠানো হয়েছে। ভেরিফাই করার পর আপনাকে গ্রুপের লিংক দেওয়া হবে।")
        del context.user_data['platform']

def main():
    Thread(target=run_flask).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_id_submission))
    
    application.run_polling()

if __name__ == '__main__':
    main()