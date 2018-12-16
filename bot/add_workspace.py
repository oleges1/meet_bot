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
    logger.info("user %s. adding workspace", user.first_name)
    update.message.reply_text('Okay, let\'s see... Tell me the name of workspace you want to join!')
    return WORKSPACE


def added_workspace(bot, update):
    user = update.message.from_user
    exist = True# check if workspace exist
    if exist:
        accessable = True # check if user has access to workspace
        if accessable:
            logger.info("user %s. workspace %s already accessable.", user.first_name, update.message.text)
            update.message.reply_text('Hey, you already can hold meetings in %s. Try again with another workspace! :)' % update.message.text)
        else:
            # add workspace for user
            logger.info("user %s. workspace %s added", user.first_name, update.message.text)
            update.message.reply_text('Great! Now you can hold meetings in %s.' % update.message.text)
    else:
        logger.info("user %s. unknown workspace %s", user.first_name, update.message.text)
        # adding workspace and updating db for user
        update.message.reply_text('It seems like I don\'t know this workspace. \
            But don\'t worry, now I know! Now you can hold meetings in %s.' % update.message.text)

    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)        
    return ACTION


workspace_states = {
    WORKSPACE: [MessageHandler(Filters.text, added_workspace)]
}
