# utils/image_processing.py
import base64
import io
from PIL import Image

def encode_image(image_bytes):
    """
    Codifica la imagen en base64.
    """
    return base64.b64encode(image_bytes).decode('utf-8')

def process_image(file_content):
    """
    Procesa la imagen: verifica el formato, redimensiona si es necesario y la codifica.
    """
    try:
        # Cargar la imagen desde los bytes
        image = Image.open(io.BytesIO(file_content))

        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Redimensionar si es mayor a 512x512
        max_size = (512, 512)
        if image.size[0] > 512 or image.size[1] > 512:
            image.thumbnail(max_size, Image.ANTIALIAS)

        # Guardar la imagen en un buffer
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        encoded_image = encode_image(buffer.getvalue())
        return encoded_image, None  # No hay error
    except Exception as e:
        return None, str(e)  # Retorna el error
