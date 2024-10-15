from jinja2 import Environment, FileSystemLoader
import os
import logging

class PromptBuilder:
    def __init__(self, meta_prompt_path=None, system_message_path=None, template_path=None, rebel_path=None, rebel2_path=None):
        # Solo cargar archivos si la ruta no es None
        self.meta_prompt_content = self.load_file(meta_prompt_path) if meta_prompt_path else None
        self.system_message = self.load_file(system_message_path) if system_message_path else None
        self.rebel_v1 = self.load_file(rebel_path) if rebel_path else None
        self.rebel_v2 = self.load_file(rebel2_path) if rebel2_path else None
        self.template = self.load_template(template_path) if template_path else None

    def load_file(self, file_path):
        """
        Cargar el contenido de un archivo. 
        Si el archivo no existe, se registra un error y se devuelve None.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            logging.info(f"Archivo cargado exitosamente: {file_path}")
            return content
        except FileNotFoundError:
            logging.error(f"No se pudo encontrar el archivo: {file_path}")
            return None
        except Exception as e:
            logging.error(f"Error al cargar el archivo {file_path}: {str(e)}")
            return None
    
    def load_template(self, path):
        """
        Cargar una plantilla usando Jinja2.
        """
        try:
            env = Environment(loader=FileSystemLoader(os.path.dirname(path)))
            template = env.get_template(os.path.basename(path))
            logging.info(f"Plantilla cargada exitosamente: {path}")
            return template
        except FileNotFoundError:
            logging.error(f"No se pudo encontrar la plantilla: {path}")
            return None
        except Exception as e:
            logging.error(f"Error al cargar la plantilla {path}: {str(e)}")
            return None

    def build_prompt(self, summarized_context, user_name, user_username, user_message, image_analysis=None):
        """
        Construir el prompt usando la plantilla cargada. 
        Los valores se reemplazan en la plantilla.
        """
        if not self.template:
            logging.error("No se pudo cargar la plantilla. No se puede construir el prompt.")
            return None
        
        # Renderizar la plantilla con los valores cargados
        return self.template.render(
            meta_prompt_content=self.meta_prompt_content or '',
            system_message=self.system_message or '',
            rebel_v1=self.rebel_v1 or '',
            rebel_v2=self.rebel_v2 or '',
            summarized_context=summarized_context,
            user_name=user_name,
            user_username=user_username,
            user_message=user_message,
            image_analysis=image_analysis or ''
        )
