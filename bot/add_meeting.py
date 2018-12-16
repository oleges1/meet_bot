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
    logger.info("user %s. creating meeting", user.first_name)

    add_user_message(update)
    update.message.reply_text('First of all, tell me nicknames of people')

    return MEETING


def add_user_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("user %s. add user %s to meeting", user.first_name, update.message.text)

    add_user_message(update)
    update.message.reply_text('Press /done if you are, else type another @name')

    return MEETING_USERS


def ask_for_time_slot(bot, update, already_used=False):
    user = update.message.from_user
    if update.message.text == end_command:
        logger.info("user %s. contestants list formed", user.first_name)

        # add_user_message(update)
        update.message.reply_text('Great! Now I need to know time you want to meet!\n'+
            'Please, send me datetime-slot in "YYYY:MM:DD-HH:MM, YYYY:MM:DD-HH:MM" or "HH:MM-HH:MM" format.\n'+
            'If it\'s without-date format, I\'ll set day as tomorrow by defaut.')
    elif already_used:
        logger.info("user %s. given time_slot is not acceptable for some users", user.first_name)

        # add_user_message(update)
        update.message.reply_text('Sorry, some users from your list already have meetings in the time you typed.\n'+
            'Please, try different time.\n')
    else:
        logger.info("user %s. given time_slot is not valid", user.first_name)

        # add_user_message(update)
        update.message.reply_text('Sorry, the time you typed has incorrect fotmat. Please, try again.\n' +
            'Remember, I need datetime-slot in "YYYY:MM:DD-HH:MM, YYYY:MM:DD-HH:MM" or "HH:MM-HH:MM" format.\n'+
            'If it\'s without-date format, I\'ll set day as tomorrow by defaut.')
    return TIME_SLOT

def ask_for_workspace(bot, update):
    user = update.message.from_user
    logger.info("user %s. time_slot got %s", user.first_name, update.message.text)
    valid_time = True # check if time_slot format is correct
    if valid_time:
        logger.info("user %s. time_slot has valid format", user.first_name)
        valid_time = True # check if time_slot is acceptable for each user
        if valid_time:
            logger.info("user %s. time_slot is acceptable for all users", user.first_name)
            update.message.reply_text("Great! Here are some workspaces you could meet in. Please, choose one or /cancel meeting.")
            # printing available workspaces
            return MEETING_WORKSPACE
        else:
            ask_for_time_slot(bot, update, True)
    else:
        ask_for_time_slot(bot, update)

def ask_for_location(bot, update):
    user = update.message.from_user
    logger.info("user %s. workspace %s selected", user.first_name, update.message.text)

    add_user_message(update)
    update.message.reply_text('Great! Here are some locations you could meet in.\n'+
        'Please, choose one or type another one I will create or /cancel meeting.')
    # printing available locations

    return MEETING_LOCATION


def added_meeting(bot, update):
    user = update.message.from_user
    logger.info("user %s. location %s selected", user.first_name, update.message.text)

    exist = True # check if location exist
    if not exist:
        # create location
        pass

    add_user_message(update)
    update.message.reply_text('Great! New meeting is added to your schedule.')
    # printing meeting info

    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return ACTION


meeting_states = {
    MEETING: [MessageHandler(Filters.text, add_user_to_meeting)],
    MEETING_USERS: [CommandHandler('done', ask_for_time_slot),
                    MessageHandler(Filters.text, add_user_to_meeting)],
    MEETING_TIME_SLOT: [MessageHandler(Filters.text, ask_for_workspace)],
    MEETING_WORKSPACE: [MessageHandler(Filters.text, ask_for_location)],
    MEETING_LOCATION: [MessageHandler(Filters.text, added_meeting)],
}
