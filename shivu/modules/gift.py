from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, Updater
import motor.motor_asyncio
from shivu import application 


client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://shuyaashivu:9fcc60263a946ef550d11406667404fa@cluster0.ikub9lo.mongodb.net/?retryWrites=true&w=majority')
db = client['Character_catcher']
user_collection = db['anime_characters_lol']

pending_gifts = {}

async def gift(update: Update, context: CallbackContext) -> None:
    sender_id = update.effective_user.id

    if not update.message.reply_to_message:
        await update.message.reply_text("You need to reply to a user's message to gift a character!")
        return

    receiver_id = update.message.reply_to_message.from_user.id
    receiver_username = update.message.reply_to_message.from_user.username
    receiver_first_name = update.message.reply_to_message.from_user.first_name

    if sender_id == receiver_id:
        await update.message.reply_text("You can't gift a character to yourself!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("You need to provide a character ID!")
        return

    character_id = context.args[0]

    sender = await user_collection.find_one({'id': sender_id})

    character = next((character for character in sender['characters'] if character['id'] == character_id), None)

    if not character:
        await update.message.reply_text("You don't have this character in your collection!")
        return

    # Add the gift offer to the pending gifts
    pending_gifts[(sender_id, receiver_id)] = {
        'character': character,
        'receiver_username': receiver_username,
        'receiver_first_name': receiver_first_name
    }

    # Create a confirmation button
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Confirm Gift", callback_data="confirm_gift")],
            [InlineKeyboardButton("Cancel Gift", callback_data="cancel_gift")]
        ]
    )

    await update.message.reply_text(f"Do you really want to gift {update.message.reply_to_message.from_user.mention}?", reply_markup=keyboard)

async def on_callback_query(update: Update, context: CallbackContext) -> None:
    sender_id = update.callback_query.from_user.id

    # Find the gift offer
    for (_sender_id, receiver_id), gift in pending_gifts.items():
        if _sender_id == sender_id:
            break
    else:
        await update.callback_query.message.reply_text("This is not for you!", show_alert=True)
        return

    if update.callback_query.data == "confirm_gift":
    
        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': receiver_id})

        
        sender['characters'].remove(gift['character'])
        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': 
        if receiver:
            await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': gift['character']}})
        else:
            
            await user_collection.insert_one({
                'id': receiver_id,
                'username': gift['receiver_username'],
                'first_name': gift['receiver_first_name'],
                'characters': [gift['character']],
            })

        
        del pending_gifts[(sender_id, receiver_id)]

        await update.callback_query.message.reply_text(f"You have successfully gifted your character to [{gift['receiver_first_name']}](tg://user?id={receiver_id})!")

GIFT_HANDLER = CommandHandler('gift', gift)
application.add_handler(GIFT_HANDLER)
application.add_handler(CallbackQueryHandler(on_callback_query, pattern='^confirm_gift$'))
