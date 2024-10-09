import tempfile
from gtts import gTTS

def text_to_voice(text, lang='es'):
    """
    Convierte texto a voz y guarda el resultado en un archivo temporal.
    
    :param text: El texto a convertir en voz
    :param lang: El idioma del texto (por defecto 'es' para español)
    :return: Un objeto NamedTemporaryFile con el audio generado
    """
    tts = gTTS(text=text, lang=lang)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file