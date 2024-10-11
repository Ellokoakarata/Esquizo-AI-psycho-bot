# Requisitos
- Python 3.8+
- Bibliotecas (instaladas a través de `requirements.txt`):
  - pyTelegramBotAPI
  - groq-client
  - google-generativeai
  - gTTS
  - openai
  - jinja2
  - requests

# Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/EsquizoAI-Psycho-Bot.git
   cd EsquizoAI-Psycho-Bot
   ```

2. Crea y activa un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   ```

3. Instala las dependencias:Y
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:
   - Crea un archivo `.env` en la raíz del proyecto o establece las variables de entorno en tu sistema:
   ```bash
   TELEGRAM_TOKEN=tu_token_de_telegram
   GROQ_API_KEY=tu_api_key_de_groq
   GOOGLE_API_KEY=tu_api_key_de_google
   ADMIN_CHAT_ID=id_del_chat_de_admin  # Opcional: para recibir notificaciones de errores
   ```
   **Nota:** Si utilizas un archivo `.env`, considera usar la biblioteca `python-dotenv` para cargar las variables automáticamente.

5. Ejecuta el bot:
   ```bash
   python bot.py
   ```

# Uso
Una vez que el bot esté en funcionamiento, puedes interactuar con él a través de Telegram.

## Comandos Disponibles:
- `/start`: Inicia la interacción con el bot.
- `/cambiar_modelo [groq|google]`: Cambia el modelo de IA utilizado por el bot.
- `/modelo_actual`: Muestra el modelo de IA actualmente en uso.
- `/modelos`: Lista los modelos disponibles.
- `/imagen [descripción]`: Genera una imagen basada en la descripción proporcionada.
- `/voz [texto]`: Convierte el texto proporcionado en un mensaje de voz.

# Personalización
## Prompts y Mensajes del Sistema:
Puedes personalizar el comportamiento y respuestas del bot modificando los archivos en la carpeta `prompts/`:
- `meta_prompt.md`: Contiene directrices generales para el comportamiento del bot.
- `system.txt`: Define el mensaje del sistema que establece el contexto para el modelo de lenguaje.
- `prompt_template.txt`: Plantilla utilizada para construir el prompt enviado al modelo de IA.

## Modelos de IA:
- **Groq (Llama)**: Asegúrate de tener una API Key válida y actualiza las configuraciones en `models/groq_model.py` si es necesario.
- **Google Generative AI**: Configura tu API Key y ajusta los parámetros en `models/google_model.py` según tus necesidades.

# Contribución
¡Las contribuciones son bienvenidas! Si deseas mejorar el bot, agregar nuevas funcionalidades o corregir errores:
1. Haz un fork del repositorio.
2. Crea una rama nueva:
   ```bash
   git checkout -b mi-nueva-funcionalidad
   ```
3. Realiza tus cambios y haz commits descriptivos.
4. Envía un pull request a la rama principal del repositorio original.

# Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más detalles.

# Contacto
Para preguntas, sugerencias o reportar problemas, puedes abrir un Issue en GitHub o contactar al mantenedor del proyecto:
- **Nombre:** [Ricardo Ruiz]
- **Correo Electrónico:** [rasricardo25@gmail.com]
- **Telegram:** [@Loko_Akrata]

# Agradecimientos
Agradecemos a todos los desarrolladores y colaboradores que han contribuido directa o indirectamente a este proyecto, y a las comunidades de código abierto que lo hacen posible. Y sobre todo a la IA.

**Nota:** Este proyecto es experimental y se proporciona "tal cual". Se recomienda revisar y entender el código antes de su implementación en entornos de producción.