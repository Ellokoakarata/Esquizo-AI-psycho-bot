# models/groq_model.py
from groq import Client
from config import GROQ_API_KEY

groq_client = Client(api_key=GROQ_API_KEY)

def generate_groq_response(prompt, history):  # Modificar para aceptar 'history'
    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-70b-versatile",
        temperature=0.88,
        max_tokens=2800,
        top_p=0.9,
        stop=None,
    )
    return chat_completion.choices[0].message.content
