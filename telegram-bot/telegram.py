import telegram.ext

token = '5828621434:AAHpD_YBVfRBDwLgxrKHdro7OjlZUyfMqvE'


def start_command(update, context):
    update.message.reply_text('Type something random to get started!')


def help_command(update, context):
    update.message.reply_text('Help')


def custom_command(update, context):
    update.message.reply_text('This is a custom command')


def handle_response(text: str) -> str:

    if 'hello' in text:
        response = 'Hello'
    elif "how are you" in text:
        response = 'You are welcome'
    else:
        response = "I don't understand"
    return response


def handle_message(update, context):
    message_type = update.message.chat.type
    text = str(update.message.text).lower()
    response = handle_response(text)
    update.message.reply_text(response)