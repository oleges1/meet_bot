import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from urllib3 import make_headers
from pony.orm import *
from pony_starting import *

db = Database()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "769890151:AAHGj9McKnhu29jJo7JaqO4Dbl0GNfRIxBk"
PROXY_URL = 'socks5://phobos.public.opennetwork.cc:1090/'
PROXY_LOGIN = '221688370'
PROXY_PASS = 'eljPzMJu'


def start(bot, update):
    keyboard = [[InlineKeyboardButton("Add meeting", callback_data='meeting')],
                [InlineKeyboardButton("Add location", callback_data='location')],
                [InlineKeyboardButton("Add workspace", callback_data='workspace')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


@db_session
def add_user(telegram_id, name):
    User(telegram_id=telegram_id, name=name)


@db_session
def get_user(telegram_id):
    return User.get(telegram_id=telegram_id)


def button(bot, update):
    query = update.callback_query
    from_user = query.from_user
    print(from_user.id, from_user.full_name)
    print(query.message.chat_id)
    user = get_user(from_user.id)
    if user is None:
        add_user(from_user.id, from_user.full_name)
    else:
        print(user.name)
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
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
