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
from dateutil import parser as dt_parser

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
                      ['Filter by time from', 'Filter by time to'],
                      ['Filter by location', 'Filter by workspace'],
                      ['Filter by participants']]
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
    return LIST_PARTICIPANTS


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

    reply_keyboard = [['No, get meetings']
                      ['Filter by time from', 'Filter by time to'],
                      ['Filter by location', 'Filter by workspace']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text(
        'Do you need to apply another filter?', reply_markup=reply_markup)
    return LIST_OF_MEETINGS


def filter_by_time_from_get(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("required filter by time from %s", user.first_name)
    update.message.reply_text(
        'Send time all meetings should be after.')
    return LIST_TIME_FROM


def filter_by_time_from_apply(bot, update):
    user = update.message.from_user
    global time
    time[0] = dt_parser.parse(update.message.text.lower().strip())
    add_user_message(update)
    logger.info("got time filter from %s: since %s", user.first_name, update.message.text)

    reply_keyboard = [['No, get meetings']
                      ['Filter by participants', 'Filter by time to'],
                      ['Filter by location', 'Filter by workspace']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text(
        'Do you need to apply another filter?', reply_markup=reply_markup)
    return LIST_OF_MEETINGS


def filter_by_time_to_get(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("required filter by time from %s", user.first_name)
    update.message.reply_text(
        'Send time all meetings should be before.')
    return LIST_TIME_TO


def filter_by_time_to_apply(bot, update):
    user = update.message.from_user
    global time
    time[1] = dt_parser.parse(update.message.text.lower().strip())
    add_user_message(update)
    logger.info("got time filter from %s: until %s", user.first_name, update.message.text)

    reply_keyboard = [['No, get meetings']
                      ['Filter by participants', 'Filter by time from'],
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
    return LIST_LOCATION


def filter_by_location_apply(bot, update):
    user = update.message.from_user
    global location
    location = update.message.text.lower().strip()
    add_user_message(update)
    logger.info("got location filter from %s: %s", user.first_name, update.message.text)

    reply_keyboard = [['No, get meetings']
                      ['Filter by time from', 'Filter by time to'],
                      ['Filter by workspace', 'Filter by participants']]
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
    return LIST_WORKSPACE

def filter_by_workspace_apply(bot, update):
    user = update.message.from_user
    global workspace
    workspace = update.message.text.lower().strip()
    add_user_message(update)
    logger.info("got workspace filter from %s: %s", user.first_name, update.message.text)

    reply_keyboard = [['No, get meetings']
                      ['Filter by time from', 'Filter by time to'],
                      ['Filter by location', 'Filter by participants']]
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
                       f'started: {meeting.start_time},\n ended: {meeting.end_time}\n\n'
        text += meeting_info
    return text


list_of_meetings_states = {
    LIST_OF_MEETINGS : [
        RegexHandler('^(Filter by participants)$', filter_by_participants_get),
        RegexHandler('^(Filter by time from)$', filter_by_time_from_get),
        RegexHandler('^(Filter by time to)$', filter_by_time_to_get),
        RegexHandler('^(Filter by location)$', filter_by_location_get),
        RegexHandler('^(Filter by workspace)$', filter_by_workspace_get),
        RegexHandler('^((No Filter)|(No, get meetings))$', get_filtered),
    ],
    LIST_PARTICIPANTS : [MessageHandler(Filters.text, filter_by_participants_apply)],
    LIST_TIME_FROM : [MessageHandler(Filters.text, filter_by_time_from_apply)],
    LIST_TIME_TO : [MessageHandler(Filters.text, filter_by_time_to_apply)],
    LIST_LOCATION : [MessageHandler(Filters.text, filter_by_location_apply)],
    LIST_WORKSPACE : [MessageHandler(Filters.text, filter_by_workspace_apply)],
}
