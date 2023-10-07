from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import random
from client import updater, dispatcher 
# Game state
game_state = {}

def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    game_state[user.id] = {
        'opponent': None,
        'choice': None,
    }
    update.message.reply_text(
        f'{user.first_name} has started a game of Rock, Paper, Scissors! Reply with /rps to accept the challenge.')

def rps(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    opponent = game_state.get(user.id)
    if opponent:
        opponent['opponent'] = user.id
        opponent['choice'] = None
        keyboard = [
            [InlineKeyboardButton("Rock", callback_data='rock'),
             InlineKeyboardButton("Paper", callback_data='paper'),
             InlineKeyboardButton("Scissors", callback_data='scissors')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f'{user.first_name} ❌ vs {opponent["name"]} ❌', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    choice = query.data
    game = game_state.get(user_id)
    if not game or not game['opponent']:
        query.edit_message_text(text="It's not your match!")
        return
    game['choice'] = choice
    opponent_game = game_state.get(game['opponent'])
    if opponent_game and opponent_game['choice']:
        # Both players have made a choice. Determine the winner.
        if game['choice'] == opponent_game['choice']:
            result = "It's a draw!"
        elif (game['choice'] == 'rock' and opponent_game['choice'] == 'scissors') or \
             (game['choice'] == 'paper' and opponent_game['choice'] == 'rock') or \
             (game['choice'] == 'scissors' and opponent_game['choice'] == 'paper'):
            result = f'{query.from_user.first_name} wins!'
        else:
            result = f'{opponent_game["name"]} wins!'
        query.edit_message_text(text=result)
    else:
        # The other player hasn't made a choice yet.
        query.edit_message_text(text=f'{query.from_user.first_name} ✅ vs {game["name"]} ❌')

updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs")
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('rps', rps))
updater.dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()

