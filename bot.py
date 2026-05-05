import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Bot ishlayapti!\n\n/play nomi yoz")

def download_audio(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        if 'entries' in info:
            info = info['entries'][0]

        filename = ydl.prepare_filename(info)
        filename = os.path.splitext(filename)[0] + ".mp3"
        title = info.get('title', 'Music')

        return filename, title

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Masalan:\n/play Eminem")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        filename, title = download_audio(query)

        with open(filename, 'rb') as audio:
            await update.message.reply_audio(audio=audio, title=title)

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

    finally:
        await msg.delete()

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
