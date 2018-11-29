#! /usr/bin/python3
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from urllib3 import make_headers
from selects import *
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
PROXY_URL = os.getenv("PROXY_URL")
PROXY_LOGIN = os.getenv("PROXY_LOGIN")
PROXY_PASS = os.getenv("PROXY_URL")


def start(bot, update):
    keyboard = [[InlineKeyboardButton("Add meeting", callback_data='meeting')],
                [InlineKeyboardButton("Add location", callback_data='location')],
                [InlineKeyboardButton("Add workspace", callback_data='workspace')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    add_user_message(update)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    from_user = query.from_user
    user = get_user(from_user.id)
    print(last_message(user).text)
    if query.data == 'meeting':
        logger.debug('meeting')
    if query.data == 'location':
        logger.debug('location')
    if query.data == 'workspace':
        logger.debug('workspace')
    bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    REQUEST_KWARGS = {
        'proxy_url': PROXY_URL,
        # Optional, if you need authentication:
        'urllib3_proxy_kwargs': {
            'headers': make_headers(proxy_basic_auth=f'{PROXY_LOGIN}:{PROXY_PASS}')
        }
    }
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN,
                      request_kwargs=REQUEST_KWARGS)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CallbackQueryHandler(button2))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
