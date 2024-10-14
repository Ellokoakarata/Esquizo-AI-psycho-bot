import os
import json
from datetime import datetime

CONVERSATION_DIR = "conversation_logs"
if not os.path.exists(CONVERSATION_DIR):
    os.makedirs(CONVERSATION_DIR)

class ConversationHistory:
    def __init__(self, user_id, max_messages=100):
        self.user_file = os.path.join(CONVERSATION_DIR, f"{user_id}.json")
        self.max_messages = max_messages
        self.history = self.load_history()

    def load_history(self):
        """
        Load the conversation history for a user. If the file doesn't exist, initialize with an empty structure.
        """
        try:
            if os.path.exists(self.user_file):
                with open(self.user_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    if isinstance(data, dict) and "messages" in data:
                        return data
            return {"messages": [], "model": "groq"}
        except Exception as e:
            print(f"Error loading history: {e}")
            return {"messages": [], "model": "groq"}

    def save_history(self):
        """
        Save the current conversation history to the user's file.
        """
        with open(self.user_file, "w", encoding="utf-8") as file:
            json.dump(self.history, file, ensure_ascii=False, indent=4)

    def add_message(self, role, content, username=None):
        """
        Add a message to the conversation history, including the role (user or bot), content, 
        optional username, and a timestamp.
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if username:
            message["username"] = username
        self.history["messages"].append(message)

        # Trim history to avoid file growing indefinitely
        self.trim_history()

    def trim_history(self):
        """
        Trim the conversation history to a set maximum number of messages.
        """
        if len(self.history["messages"]) > self.max_messages:
            self.history["messages"] = self.history["messages"][-self.max_messages:]

    def get_recent_messages(self, num_messages=5):
        """
        Get the most recent messages from the conversation history. 
        By default, it returns the last 5 messages.
        """
        return self.history["messages"][-num_messages:]
