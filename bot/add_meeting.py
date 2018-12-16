#! /usr/bin/python3
import logging
import os

from urllib3 import make_headers
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, CallbackQueryHandler,
                          Filters, RegexHandler, ConversationHandler)

from selects import *
from bot.states import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def add_meeting(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("meeting of %s: %s", user.first_name, update.message.text)

    add_user_message(update)
    update.message.reply_text('First of all, tell me @names of people')

    return MEETING


def add_user_to_meeting(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("add user to meeting: from %s, added %s",
                user.first_name, update.message.text)

    add_user_message(update)
    update.message.reply_text('Press /done if you are, else type another @name')

    return MEETING_USERS


def add_workspace_to_meeting(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("updated users list for %s", user.first_name)

    add_user_message(update)
    update.message.reply_text('Great! Now I need to know workspace!')

    return MEETING_WORKSPACE


def add_location_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("updated users list for %s", user.first_name)

    add_user_message(update)
    update.message.reply_text('Great! Now I need to know location!')

    return MEETING_LOCATION


def add_start_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("updated location for %s: %s", user.first_name, update.message.text)

    add_user_message(update)
    update.message.reply_text('Great! Now I need to know start time!')

    return MEETING_START


def add_end_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("updated start_time for %s: %s", user.first_name, update.message.text)

    add_user_message(update)
    update.message.reply_text('Great! Now I need to know end time!')

    return MEETING_END


def end_adding_meeting(bot, update):
    user = update.message.from_user
    logger.info("updated end_time for %s: %s", user.first_name, update.message.text)

    add_user_message(update)
    update.message.reply_text('Great! New meeting is added to your schedule.')

    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return ACTION


meeting_states = {
    MEETING: [MessageHandler(Filters.text, add_user_to_meeting)],
    MEETING_USERS: [CommandHandler('done', add_workspace_to_meeting),
                    MessageHandler(Filters.text, add_user_to_meeting)],
    MEETING_WORKSPACE: [MessageHandler(Filters.text, add_location_to_meeting)],
    MEETING_LOCATION: [MessageHandler(Filters.text, add_start_to_meeting)],
    MEETING_START: [MessageHandler(Filters.text, add_end_to_meeting)],
    MEETING_END: [MessageHandler(Filters.text, end_adding_meeting)]
}
