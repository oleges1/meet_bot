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

participants = list()
time = None, None
location = None
workspace = None

def list_of_meetings(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("required list of meetings from %s", user.first_name)
    global participants, time, location, workspace
    participants = list()
    time = None, None
    location = None
    workspace = None

    reply_keyboard = [['No Filter'],
                      ['Filter by time', 'Filter by participants'],
                      ['Filter by location', 'Filter by workspace']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text(
        'Do you need to apply a filter for your meetings?', reply_markup=reply_markup)
    return LIST_OF_MEETINGS

def filter_by_participants_get(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("required filter by participants from %s", user.first_name)
    update.message.reply_text(
        'Send users who must be in meeting, format: "username1 username2 ..."')
    return LIST_OF_PARTICIPANTS


def filter_by_participants_apply(bot, update):
    user = update.message.from_user
    usernames = update.message.text.lower().strip().split()
    add_user_message(update)
    logger.info("got participants to filter on from %s: %s", user.first_name, update.message.text)

    global participants
    participants = []

    all_users_exist = True
    for username in usernames:
        user = get_user_by_username(username)
        if user == None:
            logger.info("user %s does not exist", username)
            update.message.reply_text(
                'Sorry, user %s does not exist' % username)
            all_users_exist = False
        else:
            participants.append(user)

    reply_keyboard = [['No, get meetings', 'Filter by time'],
                      ['Filter by location', 'Filter by workspace']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text(
        'Do you need to apply another filter?', reply_markup=reply_markup)
    return LIST_OF_MEETINGS


def filter_by_time_get(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("required filter by time from %s", user.first_name)
    update.message.reply_text(
        'Send time borders for meeting, format: "YYYY:MM:DD-HH:MM YYYY:MM:DD-HH:MM".\n' + \
        'If you need only one border, just set second enormous big.')
    return LIST_OF_TIME


def filter_by_time_apply(bot, update):
    user = update.message.from_user
    global time
    time = update.message.text.lower().strip().split()
    add_user_message(update)
    logger.info("got time filter from %s: %s", user.first_name, update.message.text)

    reply_keyboard = [['No, get meetings', 'Filter by participants'],
                      ['Filter by location', 'Filter by workspace']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text(
        'Do you need to apply another filter?', reply_markup=reply_markup)
    return LIST_OF_MEETINGS


def filter_by_location_get(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("required filter by location from %s", user.first_name)
    update.message.reply_text(
        'Send location at which meeting could held')
    return LIST_OF_LOCATION


def filter_by_location_apply(bot, update):
    user = update.message.from_user
    global location
    location = update.message.text.lower().strip()
    add_user_message(update)
    logger.info("got location filter from %s: %s", user.first_name, update.message.text)

    reply_keyboard = [['No, get meetings', 'Filter by participants'],
                      ['Filter by time', 'Filter by workspace']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text(
        'Do you need to apply another filter?', reply_markup=reply_markup)
    return LIST_OF_MEETINGS


def filter_by_workspace_get(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("required filter by workspace from %s", user.first_name)
    update.message.reply_text(
        'Send workspace at which meeting could held')
    return LIST_OF_WORKSPACE

def filter_by_workspace_apply(bot, update):
    user = update.message.from_user
    global workspace
    workspace = update.message.text.lower().strip()
    add_user_message(update)
    logger.info("got workspace filter from %s: %s", user.first_name, update.message.text)

    reply_keyboard = [['No, get meetings', 'Filter by participants'],
                      ['Filter by location', 'Filter by time']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text(
        'Do you need to apply another filter?', reply_markup=reply_markup)
    return LIST_OF_MEETINGS

def get_filtered(bot, update):
    user = update.message.from_user
    global participants, time, location, workspace
    with db_session:
        update.message.reply_text(format_filtered(filter(user, time[0], time[1], location, workspace, participants)))


def make_list_of_users(users):
    res = ''
    for user in users:
        res += f'@{user.username} '
    return res


def format_filtered(meetings):
    text = ''
    for meeting in meetings:
        meeting_info = f'meeting_id: {meeting.id},\n meeting_name: {meeting.name},\n' + \
                       f'users: {make_list_of_users(meeting.users)},\n location: {meeting.location.name},\n ' + \
                       f'workspace: {meeting.location.workspace.name}\n ' + \
                       f'started: {meeting.start_time},\n ended: {meeting.end_time}\n'
        text += meeting_info
    return text

list_of_meetings_states = {
    LIST_OF_MEETINGS : [
        RegexHandler('^(Filter by participants)$', filter_by_participants_get),
        RegexHandler('^(Filter by time)$', filter_by_time_get),
        RegexHandler('^(Filter by location)$', filter_by_location_get),
        RegexHandler('^(Filter by workspace)$', filter_by_workspace_get),
        RegexHandler('^((No Filter)|(No, get meetings))$', get_filtered),
    ],
    LIST_OF_PARTICIPANTS : [MessageHandler(Filters.text, filter_by_participants_apply)],
    LIST_OF_TIME : [MessageHandler(Filters.text, filter_by_time_apply)],
    LIST_OF_LOCATION : [MessageHandler(Filters.text, filter_by_location_apply)],
    LIST_OF_WORKSPACE : [MessageHandler(Filters.text, filter_by_workspace_apply)],
}
