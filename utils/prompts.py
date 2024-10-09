# utils/prompts.py
from jinja2 import Environment, FileSystemLoader
import os

class PromptBuilder:
    def __init__(self, meta_prompt_path, system_message_path, template_path):
        self.meta_prompt_content = self.load_file(meta_prompt_path)
        self.system_message = self.load_file(system_message_path)
        self.template = self.load_template(template_path)

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return ''

    def load_template(self, path):
        env = Environment(loader=FileSystemLoader(os.path.dirname(path)))
        return env.get_template(os.path.basename(path))

    def build_prompt(self, summarized_context, user_name, user_username, user_message):
        return self.template.render(
            meta_prompt_content=self.meta_prompt_content,
            system_message=self.system_message,
            summarized_context=summarized_context,
            user_name=user_name,
            user_username=user_username,
            user_message=user_message
        )
