def summarize_messages(messages, max_length=1000):
    """
    Resume una lista de mensajes para que no exceda una longitud máxima.
    
    :param messages: Lista de diccionarios con los mensajes
    :param max_length: Longitud máxima del resumen
    :return: Lista resumida de mensajes
    """
    summary = []
    current_length = 0
    
    for message in reversed(messages):
        message_length = len(message['content'])
        if current_length + message_length > max_length:
            break
        summary.insert(0, message)
        current_length += message_length
    
    return summary