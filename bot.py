from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import yt_dlp
import os

# 🔹 Search natijalarni saqlash
search_results = {}

# 🔹 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot ishlayapti ✅\n\n"
        "/play nomi — tez yuklash\n"
        "/search nomi — tanlab yuklash"
    )

# 🔹 /play
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Masalan:\n/play Eminem Mockingbird")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)

            if 'entries' in info:
                info = info['entries'][0]

            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + ".mp3"
            title = info.get('title', 'Music')

        with open(filename, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio,
                title=title,
                performer="Music Bot 🎧"
            )

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")

    finally:
        await msg.delete()


# 🔍 /search
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Masalan:\n/search Eminem")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text("🔍 Qidirilmoqda...")

    try:
        ydl_opts = {
            'quiet': True,
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)

        results = info['entries']
        text = "🎵 Top 5 natija:\n\n"

        for i, video in enumerate(results):
            text += f"{i+1}. {video['title']}\n"

        search_results[update.effective_user.id] = results

        await msg.edit_text(text + "\n\n👉 Raqam yubor (1-5)")

    except Exception as e:
        await msg.edit_text(f"❌ Xatolik: {e}")


# 🎯 Tanlash (1-5 yozsa)
async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in search_results:
        return

    if not update.message.text.isdigit():
        return

    index = int(update.message.text) - 1

    if index < 0 or index >= 5:
        return

    video = search_results[user_id][index]
    url = video['webpage_url']

    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + ".mp3"

        with open(filename, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio,
                title=video['title'],
                performer="Music Bot 🎧"
            )

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")

    finally:
        await msg.delete()


# 🔹 APP
app = ApplicationBuilder().token("8710637373:AAGEPPuJe1ExB_9xAcTzkLCusJGiMrK9Y90").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))
app.add_handler(CommandHandler("search", search))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, choose))

app.run_polling()
