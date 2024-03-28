import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Function to handle the /Josuke command
async def josuke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        # If the command is followed by a video link, download the video
        video_url = ' '.join(context.args)
        await download_video(update, context, video_url)
    else:
        # If no video link is provided, send the introductory message
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="My name is Higashikata Josuke, and my Crazy Diamond can fix any video link that you send into a working video!"
        )

# Function to download video
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE, video_url):
    # Set up the yt-dlp options
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    }

    # Create a yt-dlp instance
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Download the video
            info = ydl.extract_info(video_url, download=True)

            # Get the filename and title of the downloaded video
            video_filename = ydl.prepare_filename(info)
            video_title = info.get('title', 'Video')

            # Create a keyboard button with the video title and URL
            video_url_button = InlineKeyboardButton(text=video_title, url=video_url)
            reply_markup = InlineKeyboardMarkup.from_button(video_url_button)

            # Send the downloaded video with the caption and keyboard button
            with open(video_filename, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption=video_title,
                    reply_markup=reply_markup
                )

            # Remove the downloaded video file
            os.remove(video_filename)

        except yt_dlp.utils.DownloadError as e:
            # Handle download errors
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error downloading video: {e}')

# Set up the bot and handlers
if __name__ == '__main__':
    application = ApplicationBuilder().token('Token').build()

    josuke_handler = CommandHandler('Josuke', josuke)
    application.add_handler(josuke_handler)

    application.run_polling()
