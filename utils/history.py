# utils/history.py
import os
import json

CONVERSATION_DIR = "conversation_logs"
if not os.path.exists(CONVERSATION_DIR):
    os.makedirs(CONVERSATION_DIR)

class ConversationHistory:
    def __init__(self, user_id):
        self.user_file = os.path.join(CONVERSATION_DIR, f"{user_id}.json")
        self.history = self.load_history()

    def load_history(self):
        try:
            if os.path.exists(self.user_file):
                with open(self.user_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    if isinstance(data, dict) and "messages" in data:
                        return data
            return {"messages": [], "model": "groq"}
        except Exception as e:
            print(f"Error al cargar el historial: {e}")
            return {"messages": [], "model": "groq"}

    def save_history(self):
        with open(self.user_file, "w", encoding="utf-8") as file:
            json.dump(self.history, file, ensure_ascii=False, indent=4)

    def add_message(self, role, content, username=None):
        message = {"role": role, "content": content}
        if username:
            message["username"] = username
        self.history["messages"].append(message)
