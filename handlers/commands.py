# handlers/commands.py
from utils.error_handling import handle_error
from utils.history import ConversationHistory
from config import CONVERSATION_DIR
from telebot import TeleBot
import os

def register_command_handlers(bot: TeleBot):

    @handle_error(bot)
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Bienvenido al caos de EsquizoAI. Aquí no hay órdenes, solo delirio.")

    @handle_error(bot)
    @bot.message_handler(commands=['cambiar_modelo'])
    def cambiar_modelo(message):
        user_id = str(message.chat.id)
        history = ConversationHistory(user_id)
        parts = message.text.strip().split(' ', 1)
        if len(parts) != 2:
            bot.reply_to(message, "Uso correcto: /cambiar_modelo [groq|google]")
            return
        nuevo_modelo = parts[1].lower()
        if nuevo_modelo not in ['groq', 'google']:
            bot.reply_to(message, "Modelo no reconocido. Usa 'groq' o 'google'.")
            return
        history.history['model'] = nuevo_modelo
        history.save_history()
        bot.reply_to(message, f"Modelo cambiado a **{nuevo_modelo.upper()}**.")

    @handle_error(bot)
    @bot.message_handler(commands=['modelos'])
    def listar_modelos(message):
        modelos_disponibles = "Modelos disponibles:\n" \
                              "/cambiar_modelo groq - Usar Groq (Llama)\n" \
                              "/cambiar_modelo google - Usar Google Generative AI"
        bot.reply_to(message, modelos_disponibles)

    @handle_error(bot)
    @bot.message_handler(commands=['modelo_actual'])
    def modelo_actual(message):
        user_id = str(message.chat.id)
        history = ConversationHistory(user_id)
        modelo = history.history.get('model', 'groq').upper()
        bot.reply_to(message, f"Actualmente estás usando el modelo: **{modelo}**.")

    @handle_error(bot)
    @bot.message_handler(commands=['imagen'])
    def generate_image(message):
        prompt = message.text.replace('/imagen', '').strip()
        if not prompt:
            bot.reply_to(message, "Por favor, proporciona un prompt para generar la imagen. Uso: /imagen [tu prompt]")
            return
        try:
            # Usar la API de OpenAI para generar imágenes (DALL-E)
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            image_url = response['data'][0]['url']
            bot.send_photo(message.chat.id, image_url)
        except Exception as e:
            bot.reply_to(message, "No puedo pintar el caos ahora, algo se interpuso.")
            raise e  # El decorador handle_error se encargará de manejar el error

    @handle_error(bot)
    @bot.message_handler(commands=['voz'])
    def generate_voice(message):
        text = message.text.replace('/voz', '').strip()
        if not text:
            bot.reply_to(message, "Por favor, proporciona el texto a convertir en voz. Uso: /voz [tu texto]")
            return
        try:
            temp_file = text_to_voice(text)
            with open(temp_file.name, "rb") as audio:
                bot.send_voice(message.chat.id, audio)
            os.remove(temp_file.name)
        except Exception as e:
            bot.reply_to(message, "La voz se ha ahogado en el ruido del abismo.")
            raise e
