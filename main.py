import asyncio
import logging
import replicate
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(level=logging.INFO)

# Tokens
REPLICATE_API_TOKEN = "r8_abGA4FdbA5fJvOaUSpFcA0fi5mWqtBd2YardX"
TELEGRAM_BOT_TOKEN = "8024591512:AAHDJfkd4qroZHPIcuA4mPlGg6BUVdV80U0"

client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Just send me a text prompt like `ben 10` and I’ll generate an AI image for you!")

# Handle regular text messages (image generation)
async def generate_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    if prompt.startswith("/") or not prompt:
        return

    # Step 1: Send "generating" message
    loading_msg = await update.message.reply_text("⏳ Generating image...")

    try:
        # Step 2: Fake animation (edit message repeatedly)
        for _ in range(3):  # about 6 seconds
            for dots in [".", "..", "..."]:
                await loading_msg.edit_text(f"⏳ Generating image{dots}")
                await asyncio.sleep(0.5)

        # Step 3: Run the Replicate model
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

        # Step 4: Send the final image
        await loading_msg.edit_text("✅ Image generated!")
        await update.message.reply_photo(photo=image_data, caption=f"🖼️ Prompt: {prompt}")

    except Exception as e:
        await loading_msg.edit_text(f"❌ Error: {e}")

# Run the bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handler for /start
    app.add_handler(CommandHandler("start", start))

    # Handle all regular messages as prompts
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_from_text))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
