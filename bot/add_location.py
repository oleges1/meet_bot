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
    logger.info("adding location for %s", user.first_name)
    update.message.reply_text(
        'Okay, let\'s see... Tell me the name of workspace in which new location is .. hm.. located!')
    return LOCATION


def add_location_name(bot, update):
    user = update.message.from_user
    add_user_message(update)

    logger.info("adding location for workspace %s added for %s",
                update.message.text, user.first_name)

    update.message.reply_text('Great! Now tell me the name of your location!')
    return LOCATION_NAME


def added_location(bot, update):
    user = update.message.from_user

    workspace_name = last_message(user.id).text
    add_user_message(update)

    logger.info("location %s adding for %s", update.message.text, user.first_name)

    workspace = get_workspace(workspace_name)
    if workspace is None:
        workspace = get_or_create_workspace(workspace_name)
        add_location_to_workspace(update.message.text.lower().strip(), workspace.id)
        update.message.reply_text(
            f'Great! Now you can hold meetings at {update.message.text} in new created workspace {workspace_name}')

    else:
        add_location_to_workspace(update.message.text.lower().strip(), workspace.id)
        update.message.reply_text(
            f'Great! Now you can hold meetings at {update.message.text} in workspace {workspace_name}')

    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return ACTION


location_states = {
    LOCATION: [MessageHandler(Filters.text, add_location_name)],
    LOCATION_NAME: [MessageHandler(Filters.text, added_location)]
}
