#! /usr/bin/python3
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from urllib3 import make_headers
from selects import *
import os


from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
PROXY_URL = os.getenv("PROXY_URL")
PROXY_LOGIN = os.getenv("PROXY_LOGIN")
PROXY_PASS = os.getenv("PROXY_URL")

(ACTION, LIST_OF_MEETINGS, LOCATION, WORKSPACE, MEETING,
    MEETING_USERS, MEETING_LOCATION, MEETING_START, MEETING_END) = range(9)

def start(bot, update):
    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    add_user_message(update)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)

    return ACTION

def list_of_meetings(bot, update):
    user = update.message.from_user
    logger.info("list of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('list_of_meetings')

    # return LIST_OF_MEETINGS
    return ACTION

def add_location(bot, update):
    user = update.message.from_user
    logger.info("location of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('add_location')

    # return LOCATION
    return ACTION

def add_workspace(bot, update):
    user = update.message.from_user
    logger.info("workspace of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('add_workspace')

    # return WORKSPACE
    return ACTION

def add_meeting(bot, update):
    user = update.message.from_user
    logger.info("meeting of %s: %s", user.first_name, update.message.text)

    add_user_message(update)
    update.message.reply_text('First of all, tell me @names of people')

    return MEETING


def add_user_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("add user to meeting: from %s, added %s", user.first_name, update.message.text)

    reply_keyboard = [['Done']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    add_user_message(update)
    update.message.reply_text('Press "Done" if you are, else type another @name', reply_markup=reply_markup)

    return MEETING_USERS


def add_location_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("set location to meeting: from %s, set %s", user.first_name, update.message.text)

    reply_keyboard = [['Done']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    add_user_message(update)
    update.message.reply_text('Press "Done" if you are, else type another @location', reply_markup=reply_markup)

    return MEETING_LOCATION


def add_start_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("set start_time to meeting: from %s, set %s", user.first_name, update.message.text)

    reply_keyboard = [['Done']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    add_user_message(update)
    update.message.reply_text('Press "Done" if you are, else type another @start_time', reply_markup=reply_markup)

    return MEETING_START


def add_end_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("set end_time to meeting: from %s, set %s", user.first_name, update.message.text)

    reply_keyboard = [['Done']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    add_user_message(update)
    update.message.reply_text('Press "Done" if you are, else type another @end_time', reply_markup=reply_markup)

    return MEETING_END




def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


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

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ACTION: [RegexHandler('^(My meetings)$', list_of_meetings),
                     RegexHandler('^(Add meeting)$', add_meeting),
                     RegexHandler('^(Add workspace)$', add_workspace),
                     RegexHandler('^(Add location)$', add_location),
                     RegexHandler('^((?!(My meetings)|(Add meeting)|(Add workspace)|(Add location)).)*$', start)
                     ],
            # LIST_OF_MEETINGS: [Filters.text, start],
            # WORKSPACE: [Filters.text, start],
            # LOCATION: [Filters.text, start],
            MEETING: [MessageHandler(Filters.text, add_user_to_meeting)],
            MEETING_USERS: [RegexHandler('^(Done)$', add_location_to_meeting),
                            MessageHandler(Filters.text, add_user_to_meeting)],
            # MEETING_USERS: [MessageHandler(Filters.text, add_user_to_meeting)],
            MEETING_LOCATION: [RegexHandler('^(Done)$', add_start_to_meeting),
                               RegexHandler('^((?!Done))$', add_location_to_meeting)],
            MEETING_START: [RegexHandler('^(Done)$', add_end_to_meeting),
                               RegexHandler('^((?!Done))$', add_start_to_meeting)],
            MEETING_END: [RegexHandler('^(Done)$', add_end_to_meeting),
                               RegexHandler('^((?!Done))$', add_end_to_meeting)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_error_handler(error)
    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
