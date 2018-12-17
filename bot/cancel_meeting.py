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


def make_list_of_users(users):


def cancel_meeting(bot, update, retry=False):
    user = update.message.from_user
    add_user_message(update)
    logger.info("user %s. deleting meeting", user.first_name)
    if retry:
        update.message.reply_text(
            'Let\'s try again. Send me ID of another meeting.\n' +
            'You can find one in the main menu, "My meetings". Press /cancel and then /start to go there.')
    else:
        update.message.reply_text(
            'So you want to cancel one of your meetings. Okay, just send me its ID.\n' +
            'You can find it in the main menu, "My meetings". Press /cancel and then /start to go there.')
    return DELETING


def confirm_meeting_deleting(bot, update):
    user = update.message.from_user
    add_user_message(update)

    meeting = get_meeting(update.message.text)
    if meeting is not None:
        if check_user_in_meeting(user.username, meeting.id):
            logger.info("user %s. deleting meeting %s.",
                        user.first_name, update.message.text)
            update.message.reply_text(
                'Hey, do you really want to delete this one? Just to remind...')
            meeting_info = f'meeting_id: {meeting.id},\nmeeting_name: {meeting.name},\n' + \
                           f'users: {make_list_of_users(meeting.users)},\nlocation: {meeting.location.name},\n' + \
                           f'workspace: {meeting.location.workspace.name}' + \
                           f'started: {meeting.start_time},\nended: {meeting.end_time}'
            update.message.reply_text(meeting_info)
            reply_keyboard = [['Yes', 'No']]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard)
            update.message.reply_text('So are you sure?', reply_markup=reply_markup)

            return DELETING_CONFIRMATION
        else:
            logger.info("user %s. deleting non-accessable meeting %s",
                        user.first_name, update.message.text)
            update.message.reply_text(
                'Sorry, you are not patricipate in this meeting. You have no rights to delete it.')

            reply_keyboard = [['My meetings', 'Add meeting'],
                              ['Add workspace', 'Add location'],
                              ['Cancel meeting']]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard)
            update.message.reply_text('Please choose:', reply_markup=reply_markup)
            return ACTION
    else:
        logger.info("user %s. deleting non-existing meeting %s",
                    user.first_name, update.message.text)
        update.message.reply_text('It seems like I can\'t find this meeting.\n' +
                                  'Try again with another one.')
        cancel_meeting(bot, update, retry=True)


def deleting_confirmed(bot, update):
    user = update.message.from_user
    meeting_id = last_message(user.id).text
    add_user_message(update)
    delete_meeting(meeting_id)
    logger.info('user %s. deleting meeting %s', user.first_name, meeting_id)
    update.message.reply_text(
        'Great. Meeting %s successfully deleted. See you soon!', meeting_id)

    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location'],
                      ['Cancel meeting']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return ACTION


def deleting_unconfirmed(bot, update):
    user = update.message.from_user
    add_user_message(update)
    meeting_id = 0
    logger.info('user %s. cancel deleting meeting %s', user.first_name, meeting_id)
    update.message.reply_text(
        'Great. Meeting %s remains stable. See you soon!', meeting_id)

    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location'],
                      ['Cancel meeting']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return ACTION


cancel_states = {
    DELETING: [MessageHandler(Filters.text, confirm_meeting_deleting)],
    DELETING_CONFIRMATION: [RegexHandler('^(Yes)$', deleting_confirmed),
                            RegexHandler('^(No)$', deleting_unconfirmed)]
}
