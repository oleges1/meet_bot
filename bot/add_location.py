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


def add_location(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("user %s. adding new location to db", user.first_name)
    update.message.reply_text(
        'Okay, let\'s see... Tell me the name of workspace in which new location is .. hm.. located!')
    return LOCATION


def add_location_name(bot, update):
    user = update.message.from_user
    add_user_message(update)

    workspace_name = update.message.text.lower().strip()
    workspace = get_workspace(workspace_name)
    if workspace is not None:
        logger.info("user %s. adding location for workspace %s",
                    user.first_name, update.message.text)
        update.message.reply_text('Great! Now tell me the name of your location!')
        return LOCATION_NAME
    else:
        logger.info("user %s. adding location for non-existing workspace %s",
                    user.first_name, update.message.text)
        update.message.reply_text('Sorry, mate. I don\'t know this workspace.\
            Please, create one in the main menu and try again.')

        reply_keyboard = [['My meetings', 'Add meeting'],
                          ['Add workspace', 'Add location'],
                          ['Cancel meeting']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        return ACTION


def added_location(bot, update):
    user = update.message.from_user

    workspace_name = last_message(user.id).text
    add_user_message(update)

    workspace = get_workspace(workspace_name)
    add_location_to_workspace(update.message.text.lower().strip(), workspace.id)

    logger.info("user %s. location %s added.", user.first_name, update.message.text)
    update.message.reply_text(
        'Great! Now you can hold meetings at %s in workspace %s' % (
            update.message.text, workspace_name
        ))

    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location'],
                      ['Cancel meeting']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return ACTION


location_states = {
    LOCATION: [MessageHandler(Filters.text, add_location_name)],
    LOCATION_NAME: [MessageHandler(Filters.text, added_location)]
}
