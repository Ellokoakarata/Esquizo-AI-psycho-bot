# models/groq_model.py
from groq import Client
from config import GROQ_API_KEY
import logging

# Configurar logging
logger = logging.getLogger(__name__)

groq_client = Client(api_key=GROQ_API_KEY)

def generate_groq_response(prompt, history):
    try:
        # Obtener el nombre del modelo seleccionado por el usuario
        model_name = history.history.get('model_name', 'llama')

        # Mapear el nombre del modelo a los identificadores reales
        model_mapping = {
            'llama': 'llama-3.1-70b-versatile',
            'mistral': 'mixtral-8x7b-32768'
        }

        selected_model = model_mapping.get(model_name, 'llama-3.1-70b-versatile')

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=selected_model,
            temperature=0.88,
            max_tokens=2800,
            top_p=0.9,
            stop=None,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error al generar respuesta con Groq: {e}")
        return None

def generate_groq_image_analysis(encoded_image):
    try:
        # Crear el mensaje para la API
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe detalladamente el contenido de esta imagen."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}",
                        },
                    },
                ],
            }
        ]

        # Realizar la solicitud a la API
        response = groq_client.chat.completions.create(
            messages=messages,
            model="llava-v1.5-7b-4096-preview",
        )

        # Obtener el análisis de la imagen
        image_analysis = response.choices[0].message.content
        return image_analysis

    except Exception as e:
        logger.error(f"Error al generar el análisis de imagen con Groq: {e}")
        return None
