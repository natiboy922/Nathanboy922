import os
import asyncio
import replicate
import requests
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Load from .env file
load_dotenv()

# Tokens
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Check if token exists
if not TELEGRAM_BOT_TOKEN or not REPLICATE_API_TOKEN:
    raise Exception("❌ Missing API token in .env")

# Replicate client
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# Logging
logging.basicConfig(level=logging.INFO)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! Just send a prompt like 'ben 10' or 'spiderman' and I'll generate an image for you!"
    )

# Prompt handler
async def generate_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    if prompt.startswith("/") or not prompt:
        return

    loading_msg = await update.message.reply_text("⏳ Generating image...")

    try:
        for _ in range(2):
            for dots in [".", "..", "..."]:
                await loading_msg.edit_text(f"⏳ Generating image{dots}")
                await asyncio.sleep(0.5)

        input_data = {
            "width": 768,
            "height": 768,
            "prompt": prompt,
            "refine": "expert_ensemble_refiner",
            "apply_watermark": False,
            "num_inference_steps": 25
        }

        output = client.run("stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc", input=input_data)
        image_url = str(output[0])
        image_data = requests.get(image_url).content

        await loading_msg.edit_text("✅ Image generated!")
        await update.message.reply_photo(photo=image_data, caption=f"🖼️ Prompt: {prompt}")

    except Exception as e:
        await loading_msg.edit_text(f"❌ Error generating image:\n{e}")

# Run bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_from_text))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
