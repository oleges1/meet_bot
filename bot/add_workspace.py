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


def add_workspace(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("adding workspace for %s", user.first_name)
    update.message.reply_text(
        'Okay, let\'s see... Tell me the name of workspace you want to join!')
    return WORKSPACE


def added_workspace(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("workspace %s adding for %s", update.message.text, user.first_name)

    add_user_to_workspace(user.id, update.message.text.lower().strip())
    add_workspace_to_user(user.id, update.message.text.lower().strip())

    update.message.reply_text(
        'Great! Now you can hold meetings at %s' % update.message.text)

    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return ACTION


workspace_states = {
    WORKSPACE: [MessageHandler(Filters.text, added_workspace)]
}
