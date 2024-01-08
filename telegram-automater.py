from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters, JobQueue
import json
import asyncio
import logging

# Configurations and defaults
default_config = {
    'message': 'Hello, World!',
    'interval': 5,  # in minutes
    'format': 'plain',  # could be 'markdown' or 'html'
    'chat_ids': []  # Initialize an empty list for chat IDs
}
config = default_config.copy()

# Enable logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# logger = logging.getLogger(__name__)

# Save and load configurations to a file
def save_config():
    with open('config.json', 'w') as f:
        json.dump(config, f)
    print("Configuration saved.")

def load_config():
    global config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Configuration file not found, creating new one.")
        save_config()
# Assume we have a global variable 'config' that contains a list of chat IDs
# config['chat_ids'] = []

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("get_chat_id called")
        chat_id = update.message.chat_id
        print(f"Chat ID: {chat_id}")
        message = f"The chat ID is {chat_id}"
        if chat_id not in config['chat_ids']:
            config['chat_ids'].append(chat_id)
            save_config()
            message += " and has been saved."
        await context.bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Error in get_chat_id: {e}")
        
##################################################################################################################

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    print(f"Message received in chat: {chat_id}")
    if chat_id < 0:  # group chat IDs are negative
        if chat_id not in config['chat_ids']:
            config['chat_ids'].append(chat_id)
            save_config()
            print(f"Added new group chat ID: {chat_id}")
        await context.bot.send_message(chat_id=chat_id, text="Bot is now active in this group.")
            
##################################################################################################################

async def broadcast_to_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for chat_id in config['chat_ids']:
        try:
            await context.bot.send_message(chat_id=chat_id, text=config['message'])
        except Exception as e:
            print(f"Failed to send message to chat ID {chat_id}: {e}")
            
###################################################################################################################

async def add_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # This function could be called when the user sends a command like /addchat
    chat_id = update.message.chat_id
    if chat_id not in config['chat_ids']:
        config['chat_ids'].append(chat_id)
        save_config()
        await update.message.reply_text('This chat has been added to the list of recipients.')
    else:
        await update.message.reply_text('This chat is already in the list of recipients.')
        
#####################################################################################################################
        
async def send_message_to_group(context: ContextTypes.DEFAULT_TYPE, chat_id, text):
    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
        print(f"Sent message to group {chat_id}")
    except Exception as e:
        print(f"Error: Could not send message to chat_id {chat_id}: {e}")
        
async def automated_message_task(context):
    while True:
        for chat_id in config['chat_ids']:
            try:
                await context.bot.send_message(chat_id=chat_id, text=config['message'])
                print(f"Sent message to chat ID {chat_id}")
            except Exception as e:
                print(f"Failed to send message to chat ID {chat_id}: {e}")
        await asyncio.sleep(config['interval'] * 60) 

async def send_message_to_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # This function sends a message to all chats in 'config['chat_ids']'
    message_to_send = "This is a test message."
    for chat_id in config['chat_ids']:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message_to_send)
        except Exception as e:
            # Handle the exception appropriately
            print(f"Error: Could not send message to chat_id {chat_id}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    load_config()
    keyboard = [
        [InlineKeyboardButton("Update Message", callback_data='update_message')],
        [InlineKeyboardButton("Change Interval", callback_data='change_interval')],
        [InlineKeyboardButton("Format Message", callback_data='format_message')],
        [InlineKeyboardButton("View Current Config", callback_data='view_config')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose:', reply_markup=reply_markup)
    
    print("Bot started by user:", update.effective_user.username)
    
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    if chat_id not in config['chat_ids']:
        config['chat_ids'].append(chat_id)
        save_config()
        print(f"New chat ID saved: {chat_id}")
    await context.bot.send_message(chat_id=chat_id, text=f"The chat ID is {chat_id}")
    
async def print_chat_ids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Current saved chat IDs:")
    for chat_id in config['chat_ids']:
        print(chat_id)
    await update.message.reply_text("Chat IDs printed in the console.")
    
async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Implement the logic for sending a file. For example, you might ask the user to send the file.
    await update.message.reply_text('Please send me the file you want to upload.')
    
async def list_chat_ids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_ids = ', '.join(str(id) for id in config['chat_ids'])
    await update.message.reply_text(f"Saved chat IDs: {chat_ids}")
    

async def send_test_message_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    group_chat_id = update.message.chat_id  # Replace this with your actual group chat ID
    try:
        await context.bot.send_message(chat_id=group_chat_id, text="Test message to the group")
        print(f"Message sent to group {group_chat_id}")
    except Exception as e:
        print(f"Error: Could not send message to chat_id {group_chat_id}: {e}")
        


async def reset_to_defaults(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Reset configuration to default and save.
    global config
    config = default_config.copy()
    save_config()
    print("Configuration reset to defaults.")
    await update.message.reply_text('Configuration has been reset to defaults.')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'update_message':
        context.user_data['choice'] = 'message'
        await query.edit_message_text(text='Send me the new message.')
        
    elif query.data == 'send_file':
        await send_file(update, context)

    elif query.data == 'reset':
        await reset_to_defaults(update, context)

    elif query.data == 'change_interval':
        context.user_data['choice'] = 'interval'
        await query.edit_message_text(text='Send me the new interval (in minutes).')

    elif query.data == 'format_message':
        context.user_data['choice'] = 'format'
        await query.edit_message_text(text='Choose the message format:',
                                      reply_markup=format_keyboard())

    elif query.data == 'view_config':
        load_config()
        message = f"Current Configuration:\nMessage: {config['message']}\n" \
                  f"Interval: {config['interval']} minutes\nFormat: {config['format']}"
        await query.edit_message_text(text=message)
        
# Define `your_file_handler_function` to handle file uploads
async def your_file_handler_function(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get the file from the update
    document = update.message.document
    # You can download the file as follows, or forward it, or just get the file_id.
    file = await context.bot.get_file(document.file_id)
    # For example, download the file:
    file_path = f'/path/to/download/directory/{document.file_name}'
    await file.download(file_path)
    # Reply to the user
    await update.message.reply_text(f'The file has been saved as {document.file_name}')


def format_keyboard():
    print("Format keyboard displayed.")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Plain", callback_data='format_plain')],
        [InlineKeyboardButton("Markdown", callback_data='format_markdown')],
        [InlineKeyboardButton("HTML", callback_data='format_html')],
    ])
    

async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    text = update.message.text
    
    print("Received information from user:", update.effective_user.username)

    if user_data['choice'] == 'message':
        config['message'] = text
        await update.message.reply_text(f'Message updated to: {text}')
    elif user_data['choice'] == 'interval':
        try:
            interval = int(text)
            config['interval'] = interval
            await update.message.reply_text(f'Interval updated to: {interval} minutes')
        except ValueError:
            await update.message.reply_text('Please send a number for the interval.')
            return

    save_config()
    

async def format_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    load_config()
    
    if query.data.startswith('format_'):
        _, format_type = query.data.split('_')
        config['format'] = format_type
        save_config()
        await query.edit_message_text(text=f'Message format updated to: {format_type}')

if __name__ == '__main__':
    
    try:
        print("Starting bot...")
        # Your bot setup and polling start here
    except Exception as e:
        print(f"An error occurred: {e}")
    # Load or initialize configuration
    load_config()
    
    # Create the application and pass it your bot's token.
    application = Application.builder().token("------").build()
    
    application.add_handler(CommandHandler('getchatid', get_chat_id))
    
    application.add_handler(CommandHandler('printchatids', print_chat_ids))
    
    # Add the command handler in the main function
    application.add_handler(CommandHandler('listchatids', list_chat_ids))
    
    # Add the command handler in the main function
    application.add_handler(CommandHandler('testtogroup', send_test_message_to_group))
    
    application.add_handler(CommandHandler('broadcast', broadcast_to_groups))
    
    # Add a MessageHandler for documents if you want to handle file uploads.
    application.add_handler(MessageHandler(filters.Document.ALL, your_file_handler_function))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Add handlers to the application
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CallbackQueryHandler(format_button, pattern='^format_.*$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, received_information))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()