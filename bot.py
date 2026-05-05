import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# download function
def download_audio(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)

        if 'entries' in info:
            info = info['entries'][0]

        filename = ydl.prepare_filename(info)
        filename = os.path.splitext(filename)[0] + ".mp3"
        title = info.get('title', 'Music')

    return filename, title


# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎧 Ultimate Music Bot\n\n"
        "/play nomi — tez yuklash\n"
        "/search nomi — tanlab yuklash\n"
        "Link tashlasang ham ishlaydi (YouTube / TikTok)"
    )


# play
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Masalan:\n/play Eminem")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        filename, title = download_audio(f"ytsearch:{query}")

        with open(filename, 'rb') as audio:
            await update.message.reply_audio(audio=audio, title=title)

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

    await msg.delete()


# search (inline button)
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Masalan:\n/search Eminem")
        return

    query = " ".join(context.args)

    ydl = yt_dlp.YoutubeDL({'quiet': True})
    info = ydl.extract_info(f"ytsearch5:{query}", download=False)

    buttons = []
    for i in info['entries']:
        buttons.append([
            InlineKeyboardButton(i['title'][:40], callback_data=i['webpage_url'])
        ])

    await update.message.reply_text(
        "🎵 Tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# button click
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = query.data
    msg = await query.message.reply_text("⏳ Yuklanmoqda...")

    try:
        filename, title = download_audio(url)

        with open(filename, 'rb') as audio:
            await query.message.reply_audio(audio=audio, title=title)

        os.remove(filename)

    except Exception as e:
        await query.message.reply_text(f"❌ {e}")

    await msg.delete()


# link handler (yt / tt / insta)
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "http" not in url:
        return

    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        filename, title = download_audio(url)

        with open(filename, 'rb') as audio:
            await update.message.reply_audio(audio=audio, title=title)

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

    await msg.delete()


# main
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("search", search))

    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("🔥 Bot ishlayapti...")
    app.run_polling()


if __name__ == "__main__":
    main()
