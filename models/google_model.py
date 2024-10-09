# models/google_model.py
import google.generativeai as genai
from config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)

def serialize_google_chat_history(chat_history):
    serialized_history = []
    for message in chat_history:
        if isinstance(message, dict):
            serialized_message = message
        else:
            serialized_message = {
                "role": message.role if hasattr(message, 'role') else "user",
                "parts": []
            }
            if hasattr(message, 'parts'):
                for part in message.parts:
                    if hasattr(part, 'text'):
                        serialized_message["parts"].append({"text": part.text})
                    elif isinstance(part, str):
                        serialized_message["parts"].append({"text": part})
            elif hasattr(message, 'content'):
                serialized_message["parts"].append({"text": message.content})
        serialized_history.append(serialized_message)
    return serialized_history

def generate_google_response(prompt, history):
    # Configuración del modelo de Google Generative AI
    model_name = 'models/gemini-1.5-flash-002'
    harassment_setting = 'block_none'
    temperature = 0.66
    top_p = 1
    top_k = 1
    max_output_tokens = 1024

    model = genai.GenerativeModel(
        model_name=model_name,
        safety_settings={'HARASSMENT': harassment_setting},
        generation_config={
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_output_tokens
        }
    )

    # Recuperar o iniciar una sesión de chat
    chat = model.start_chat(history=history.history.get('google_chat_history', []))

    try:
        response = chat.send_message(prompt)
        if response.text:
            reply_content = response.text
        else:
            raise ValueError("No se generó ninguna respuesta válida.")
    except genai.types.BlockedPromptException:
        reply_content = "Lo siento, no puedo generar una respuesta para eso debido a restricciones de contenido."
    except Exception as e:
        reply_content = f"Error al generar respuesta: {str(e)}"

    # Actualizar el historial de chat de Google
    history.history['google_chat_history'] = serialize_google_chat_history(chat.history)
    history.save_history()

    return reply_content
