from jinja2 import Environment, FileSystemLoader
import os
import logging

class PromptBuilder:
    def __init__(self, meta_prompt_path, system_message_path, template_path, rebel_path, rebel2_path ):
        self.meta_prompt_content = self.load_file(meta_prompt_path)
        self.system_message = self.load_file(system_message_path)
        self.rebel_v1 = self.load_file(rebel_path)
        self.rebel_v2 = self.load_file(rebel2_path)
        self.template = self.load_template(template_path)

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            logging.info(f"Archivo cargado exitosamente: {file_path}")
            return content
        except FileNotFoundError:
            logging.error(f"No se pudo encontrar el archivo: {file_path}")
            return ''
        except Exception as e:
            logging.error(f"Error al cargar el archivo {file_path}: {str(e)}")
            return ''
    
    def load_template(self, path):
        env = Environment(loader=FileSystemLoader(os.path.dirname(path)))
        return env.get_template(os.path.basename(path))

    def build_prompt(self, summarized_context, user_name, user_username, user_message):
        return self.template.render(
            meta_prompt_content=self.meta_prompt_content,
            system_message=self.system_message,
            rebel_v1=self.rebel_v1,
            rebel_v2=self.rebel_v2,
            summarized_context=summarized_context,
            user_name=user_name,
            user_username=user_username,
            user_message=user_message
        )
