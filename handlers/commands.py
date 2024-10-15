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
        user_id = str(message.from_user.id)  # Usar from_user.id para obtener el ID del usuario
        history = ConversationHistory(user_id)
        parts = message.text.strip().split()
        if len(parts) < 2:
            bot.reply_to(message, "Correct usage: /change_model [groq|google] [model_name (optional)]")
            return
        model_provider = parts[1].lower()
        if model_provider not in ['groq', 'google']:
            bot.reply_to(message, "Unrecognized model provider. Use 'groq' or 'google'.")
            return

        # Manejar sub-modelos para Groq
        model_name = None
        if model_provider == 'groq':
            if len(parts) == 3:
                model_name = parts[2].lower()
                if model_name not in ['llama', 'mistral']:
                    bot.reply_to(message, "Unrecognized Groq model. Use 'llama' or 'mistral'.")
                    return
            else:
                # Si no se especifica, usar 'llama' por defecto
                model_name = 'llama'

        # Guardar en el historial
        history.history['model_provider'] = model_provider
        history.history['model_name'] = model_name
        history.save_history()

        if model_provider == 'groq':
            bot.reply_to(message, f"Model changed to **Groq - {model_name.upper()}**.")
        else:
            bot.reply_to(message, f"Model changed to **{model_provider.upper()}**.")

    @handle_error(bot)
    @bot.message_handler(commands=['models'])
    def list_models(message):
        available_models = (
            "Available models:\n"
            "/change_model groq llama - Use Groq Llama model\n"
            "/change_model groq mistral - Use Groq Mistral model\n"
            "/change_model google - Use Google Generative AI\n"
            "\n"
            "Example usages:\n"
            "/change_model groq llama\n"
            "/change_model groq mistral\n"
            "/change_model google"
        )
        bot.reply_to(message, available_models)

    @handle_error(bot)
    @bot.message_handler(commands=['current_model'])
    def current_model(message):
        user_id = str(message.from_user.id)
        history = ConversationHistory(user_id)
        model_provider = history.history.get('model_provider', 'groq').upper()
        model_name = history.history.get('model_name', '').upper()
        if model_provider == 'GROQ' and model_name:
            bot.reply_to(message, f"You are currently using the model: **{model_provider} - {model_name}**.")
        else:
            bot.reply_to(message, f"You are currently using the model: **{model_provider}**.")

    @handle_error(bot)
    @bot.message_handler(commands=['help'])
    def help_command(message):
        help_text = (
            "Available commands:\n"
            "/start - Start interacting with the bot\n"
            "/help - Show this help message\n"
            "/change_model [provider] [model_name] - Change the AI model\n"
            "/models - List available models\n"
            "/current_model - Show the current model you are using\n"
            "/image [prompt] - Generate an image based on a prompt\n"
            "/voice [text] - Convert text to voice\n"
        )
        bot.reply_to(message, help_text)

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
