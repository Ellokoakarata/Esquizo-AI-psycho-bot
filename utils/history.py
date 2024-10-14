import os
import json
from datetime import datetime

CONVERSATION_DIR = "conversation_logs"
if not os.path.exists(CONVERSATION_DIR):
    os.makedirs(CONVERSATION_DIR)

class ConversationHistory:
    def __init__(self, user_id, max_messages=100):
        self.user_dir = os.path.join(CONVERSATION_DIR, str(user_id))  # Directorio por user_id
        if not os.path.exists(self.user_dir):
            os.makedirs(self.user_dir)

        self.max_messages = max_messages
        self.user_file = self.get_daily_file()  # Archivo para el día actual
        self.history = self.load_history()

    def get_daily_file(self):
        """
        Devuelve la ruta del archivo JSON del historial basado en la fecha actual.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")  # Formato de fecha YYYY-MM-DD
        return os.path.join(self.user_dir, f"{current_date}.json")

    def load_history(self):
        """
        Cargar el historial de conversaciones del archivo diario. Si el archivo no existe, se inicializa con una estructura vacía.
        """
        try:
            if os.path.exists(self.user_file):
                with open(self.user_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    if isinstance(data, dict) and "messages" in data:
                        return data
            return {"messages": [], "model": "groq"}  # Historial vacío si no existe
        except Exception as e:
            print(f"Error loading history: {e}")
            return {"messages": [], "model": "groq"}

    def save_history(self):
        """
        Guardar el historial de conversaciones actual en el archivo diario del usuario.
        """
        with open(self.user_file, "w", encoding="utf-8") as file:
            json.dump(self.history, file, ensure_ascii=False, indent=4)

    def add_message(self, role, content, username=None):
        """
        Agregar un mensaje al historial de conversación, incluyendo el rol (user o assistant), el contenido,
        el nombre de usuario opcional y la marca de tiempo.
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if username:
            message["username"] = username
        self.history["messages"].append(message)

        # Recortar el historial si es necesario
        self.trim_history()

        # Guardar el historial actualizado
        self.save_history()

    def trim_history(self):
        """
        Recortar el historial de conversaciones para mantener un máximo de mensajes.
        """
        if len(self.history["messages"]) > self.max_messages:
            self.history["messages"] = self.history["messages"][-self.max_messages:]

    def get_recent_messages(self, num_messages=3):
        """
        Obtener los mensajes más recientes del historial de conversaciones.
        """
        return self.history["messages"][-num_messages:]
