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

def list_of_meetings(bot, update):
    user = update.message.from_user
    logger.info("required list of meetings from %s", user.first_name)

    reply_keyboard = [['No Filter'],
                      ['Filter by time', 'Filter by participants'],
                      ['Filter by location', 'Filter by workspace']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text(
        'Do you need to apply a filter for your meetings?', reply_markup=reply_markup)
    return LIST_OF_MEETINGS

def filter_by_participants(bot, update):
    user = update.message.from_user
    
