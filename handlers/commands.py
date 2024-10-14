from utils.error_handling import handle_error
from utils.history import ConversationHistory
from config import CONVERSATION_DIR
from telebot import TeleBot
import os

def register_command_handlers(bot: TeleBot):

    @handle_error(bot)
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Welcome to the chaos of EsquizoAI. There are no orders here, only delirium.")

    @handle_error(bot)
    @bot.message_handler(commands=['change_model'])
    def change_model(message):
        user_id = str(message.chat.id)
        history = ConversationHistory(user_id)
        parts = message.text.strip().split(' ', 1)
        if len(parts) != 2:
            bot.reply_to(message, "Correct usage: /change_model [groq|google]")
            return
        new_model = parts[1].lower()
        if new_model not in ['groq', 'google']:
            bot.reply_to(message, "Unrecognized model. Use 'groq' or 'google'.")
            return
        history.history['model'] = new_model
        history.save_history()
        bot.reply_to(message, f"Model changed to **{new_model.upper()}**.")

    @handle_error(bot)
    @bot.message_handler(commands=['models'])
    def list_models(message):
        available_models = "Available models:\n" \
                           "/change_model groq - Use Groq (Llama)\n" \
                           "/change_model google - Use Google Generative AI"
        bot.reply_to(message, available_models)

    @handle_error(bot)
    @bot.message_handler(commands=['current_model'])
    def current_model(message):
        user_id = str(message.chat.id)
        history = ConversationHistory(user_id)
        model = history.history.get('model', 'groq').upper()
        bot.reply_to(message, f"You are currently using the model: **{model}**.")

    @handle_error(bot)
    @bot.message_handler(commands=['image'])
    def generate_image(message):
        prompt = message.text.replace('/image', '').strip()
        if not prompt:
            bot.reply_to(message, "Please provide a prompt to generate the image. Usage: /image [your prompt]")
            return
        try:
            # Use OpenAI's API to generate images (DALL-E)
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            image_url = response['data'][0]['url']
            bot.send_photo(message.chat.id, image_url)
        except Exception as e:
            bot.reply_to(message, "I cannot paint chaos right now, something stands in the way.")
            raise e  # The handle_error decorator will handle the error

    @handle_error(bot)
    @bot.message_handler(commands=['voice'])
    def generate_voice(message):
        text = message.text.replace('/voice', '').strip()
        if not text:
            bot.reply_to(message, "Please provide the text to convert to voice. Usage: /voice [your text]")
            return
        try:
            temp_file = text_to_voice(text)
            with open(temp_file.name, "rb") as audio:
                bot.send_voice(message.chat.id, audio)
            os.remove(temp_file.name)
        except Exception as e:
            bot.reply_to(message, "The voice has drowned in the noise of the abyss.")
            raise e
