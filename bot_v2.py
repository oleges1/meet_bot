#! /usr/bin/python3
import logging
import os
from urllib3 import make_headers
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, CallbackQueryHandler,
                          Filters, RegexHandler, ConversationHandler)

from bot.my_meetings import *
from bot.add_meeting import *
from bot.add_workspace import *
from bot.add_location import *
from bot.cancel_meeting import *
from bot.states import *

import os

TOKEN = os.getenv("TOKEN")
PROXY_URL = os.getenv("PROXY_URL")
PROXY_LOGIN = os.getenv("PROXY_LOGIN")
PROXY_PASS = os.getenv("PROXY_URL")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(bot, update):
    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location'],
                      ['Cancel meeting']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    add_user_message(update)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return ACTION


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! Come again to check your meetings!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    REQUEST_KWARGS = {
        'proxy_url': PROXY_URL,
        'urllib3_proxy_kwargs': {
            'headers': make_headers(proxy_basic_auth=f'{PROXY_LOGIN}:{PROXY_PASS}')
        }
    }
    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ACTION: [RegexHandler('^(My meetings)$', list_of_meetings),
                     RegexHandler('^(Add meeting)$', add_meeting),
                     RegexHandler('^(Add workspace)$', add_workspace),
                     RegexHandler('^(Add location)$', add_location),
                     RegexHandler('^(Cancel meeting)$', cancel_meeting),
                     RegexHandler(
                         '^((?!(My meetings)|(Add meeting)|(Add workspace)|(Add location)|(Cancel meeting)).)*$', start)
                     ]
        },

        fallbacks=[CommandHandler('cancel', cancel),
                   CommandHandler('help', help)]
    )
    # conv_handler.states.update(list_of_meetings_states)
    conv_handler.states.update(workspace_states)
    conv_handler.states.update(cancel_states)
    conv_handler.states.update(meeting_states)
    conv_handler.states.update(location_states)
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
