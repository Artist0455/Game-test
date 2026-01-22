import os
import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token (Get from @BotFather)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Sample Celebrities Database
CELEBRITIES = [
    "Shah Rukh Khan",
    "Salman Khan", 
    "Amitabh Bachchan",
    "Aamir Khan",
    "Virat Kohli",
    "MS Dhoni",
    "Tom Cruise",
    "Leonardo DiCaprio",
    "Deepika Padukone",
    "Priyanka Chopra"
]

# Store current game for each chat
current_game = {}

# Function to generate celebrity image
def create_celebrity_image(celebrity_name: str):
    """Create a test image with celebrity name"""
    # Create image with random background color
    colors = [
        (41, 128, 185),   # Blue
        (39, 174, 96),    # Green
        (142, 68, 173),   # Purple
        (230, 126, 34),   # Orange
        (231, 76, 60),    # Red
    ]
    bg_color = random.choice(colors)
    
    img = Image.new('RGB', (500, 500), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a nice font
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Add celebrity name
    text = celebrity_name
    draw.text((250, 200), text, fill='white', font=font, anchor="mm")
    
    # Add "Guess Me!" text
    draw.text((250, 300), "Guess Me!", fill='yellow', font=font, anchor="mm")
    
    # Add decorative elements
    draw.rectangle([100, 100, 400, 400], outline='white', width=3)
    
    # Convert to bytes
    img_byte_array = BytesIO()
    img.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)
    
    return img_byte_array

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    welcome_text = """
🎬 *Celebrity Guess Bot* 🎬

Simply guess the celebrity name!

🤔 *How to Play:*
1. Use /check to get a celebrity photo
2. Type the celebrity name in chat
3. Bot will tell you if you're correct!

🎯 *Example:*
/check (get photo)
Then type: "Shah Rukh Khan"

Let's get started! 🚀
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a celebrity photo"""
    chat_id = update.effective_chat.id
    
    # Select random celebrity
    celebrity = random.choice(CELEBRITIES)
    
    # Generate image
    photo = create_celebrity_image(celebrity)
    
    # Store the correct answer for this chat
    current_game[chat_id] = celebrity.lower()
    
    # Send photo
    await update.message.reply_photo(
        photo=photo,
        caption=f"🎬 *Who is this celebrity?*\n\nType your guess in chat!",
        parse_mode='Markdown'
    )
    
    logger.info(f"Sent photo for {celebrity} to chat {chat_id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (guesses)"""
    chat_id = update.effective_chat.id
    user_guess = update.message.text.strip().lower()
    
    # Check if there's an active game in this chat
    if chat_id not in current_game:
        return
    
    correct_answer = current_game[chat_id]
    
    # Check if guess is correct
    if user_guess == correct_answer.lower():
        response = f"🎉 *CORRECT!* 🎉\n\n✅ It's *{correct_answer.title()}*!\n\nUse /check for another celebrity!"
        
        # Remove the game so user needs to /check again
        del current_game[chat_id]
    else:
        # Give hint for wrong guesses
        words = correct_answer.split()
        if len(words) > 1:
            # Show first letters as hint
            hint = ' '.join([word[0].upper() + '***' for word in words])
            response = f"❌ Not quite! Hint: {hint}\n\nTry again!"
        else:
            # Show first and last letter for single word names
            hint = correct_answer[0].upper() + '***' + correct_answer[-1].upper()
            response = f"❌ Wrong! Hint: {hint}\n\nTry again!"
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def answer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the correct answer"""
    chat_id = update.effective_chat.id
    
    if chat_id not in current_game:
        await update.message.reply_text("No active game! Use /check first.")
        return
    
    answer = current_game[chat_id]
    await update.message.reply_text(f"🔍 The answer is: *{answer.title()}*\n\nUse /check for new game.", parse_mode='Markdown')
    
    # Remove game after showing answer
    del current_game[chat_id]

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    help_text = """
🆘 *Help - Celebrity Guess Bot*

📌 *Commands:*
/start - Welcome message
/check - Get a celebrity photo to guess
/answer - Reveal the answer
/help - This message

🎮 *How to play:*
1. Type /check to get a photo
2. Type the celebrity's name in chat
3. Bot will tell you if you're right!

💡 *Tips:*
- Names are case-insensitive
- Use full names (e.g., "Shah Rukh Khan")
- You can try multiple times

Example:
/check → (gets photo)
You type: "Tom Cruise"
Bot: 🎉 CORRECT!

Happy guessing! 🎬
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    """Start the bot"""
    # Create Application
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("answer", answer_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Handle text messages (guesses)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("🤖 Bot is running... Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
