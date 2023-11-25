import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram.ext import MessageHandler, filters
from telegram.ext import CommandHandler
from shivu import application 
from shivu import db, GROUP_ID, OWNER_ID 
from shivu import PHOTO_URL, SUPPORT_CHAT, UPDATE_CHAT 
import random
collection = db['total_pm_users']


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:
        
        await collection.insert_one({"_id": user_id, "first_name": first_name, "username": username})
        
        await context.bot.send_message(chat_id=GROUP_ID, text=f"<a href='tg://user?id={user_id}'>{first_name}</a> STARTED THE BOT", parse_mode='HTML')
    else:
        
        if user_data['first_name'] != first_name or user_data['username'] != username:
            
            await collection.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username}})

    

    if update.effective_chat.type== "private":
        
        
        caption = f"""
        ***𝗛𝗼𝗹𝗮 𝗛𝗼𝗹𝗮! {update.effective_user.first_name} ✨***

***ᴇᴍʙᴀʀᴋ ᴏɴ ᴀɴ ᴇxʜɪʟᴀʀᴀᴛɪɴɢ ᴊᴏᴜʀɴᴇʏ ᴛʜʀᴏᴜɢʜ ᴛʜᴇ ᴡᴏʀʟᴅ ᴏꜰ ᴀɴɪᴍᴇ! ɪ'ᴍ ʏᴏᴜʀ ɢᴜɪᴅᴇ ᴛᴏ ᴄᴀᴘᴛᴜʀɪɴɢ ᴀɴᴅ ᴄᴏʟʟᴇᴄᴛɪɴɢ ᴀ ᴅɪᴠᴇʀꜱᴇ ᴀʀʀᴀʏ ᴏꜰ ᴠɪʙʀᴀɴᴛ ᴄʜᴀʀᴀᴄᴛᴇʀꜱ. ᴇɴɢᴀɢᴇ ɪɴ ᴄʜᴀʟʟᴇɴɢᴇꜱ, ᴛʀᴀᴅᴇ ᴡɪᴛʜ ꜰᴇʟʟᴏᴡ ᴇɴᴛʜᴜꜱɪᴀꜱᴛꜱ, ᴀɴᴅ ʙᴜɪʟᴅ ʏᴏᴜʀ ᴜʟᴛɪᴍᴀᴛᴇ ᴀɴɪᴍᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ. ʟᴇᴛ'ꜱ ᴅɪᴠᴇ ɪɴᴛᴏ ᴛʜɪꜱ ᴀᴅᴠᴇɴᴛᴜʀᴇ ᴛᴏɢᴇᴛʜᴇʀ***
               """
        keyboard = [
            [InlineKeyboardButton("+ Sᴛᴀʀᴛ Gʀᴀʙʙɪɴɢ +", url=f'http://t.me/CatchEmWaifuBot?startgroup=new')],
             [InlineKeyboardButton("🏥 Sᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{SUPPORT_CHAT}'),
            InlineKeyboardButton("📘 Uᴘᴅᴀᴛᴇꜱ", url=f'https://t.me/{UPDATE_CHAT}')],
            [InlineKeyboardButton("⚙ Hᴇʟᴘ", callback_data='help')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        photo_url = random.choice(PHOTO_URL)

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

    else:
        photo_url = random.choice(PHOTO_URL)
        keyboard = [
            
            [InlineKeyboardButton("🏥 Sᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{SUPPORT_CHAT}'),
            InlineKeyboardButton("📘 Uᴘᴅᴀᴛᴇꜱ", url=f'https://t.me/{UPDATE_CHAT}')],
            [InlineKeyboardButton("+ ᴀᴅᴅ ᴍᴇ ᴛᴏ ɢʀᴏᴜᴘ +", url=f'http://t.me/CatchEmWaifuBot?startgroup=new')],

        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption="ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ",reply_markup=reply_markup )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """
    ***Gᴇᴛ Hᴇʟᴘ :***
    
***/guess: To Guess character (only works in group)***
***/fav: Add Your fav***
***/trade : To trade Characters***
***/gift: Give any Character from Your Collection to another user.. (only works in groups)***
***/collection: To see Your Collection***
***/topgroups : See Top Groups.. Ppl Guesses Most in that Groups***
***/top: Too See Top Users***
***/ctop : Your ChatTop***
***/changetime: Change Character appear time (only works in Groups)***
   """
        help_keyboard = [[InlineKeyboardButton("⤾ Bᴀᴄᴋ", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)
        
        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':

        caption = f"""
        ***𝗛𝗼𝗹𝗮 𝗛𝗼𝗹𝗮! {update.effective_user.first_name}*** ✨

***​ᴇᴍʙᴀʀᴋ ᴏɴ ᴀɴ ᴇxʜɪʟᴀʀᴀᴛɪɴɢ ᴊᴏᴜʀɴᴇʏ ᴛʜʀᴏᴜɢʜ ᴛʜᴇ ᴡᴏʀʟᴅ ᴏꜰ ᴀɴɪᴍᴇ! ɪ'ᴍ ʏᴏᴜʀ ɢᴜɪᴅᴇ ᴛᴏ ᴄᴀᴘᴛᴜʀɪɴɢ ᴀɴᴅ ᴄᴏʟʟᴇᴄᴛɪɴɢ ᴀ ᴅɪᴠᴇʀꜱᴇ ᴀʀʀᴀʏ ᴏꜰ ᴠɪʙʀᴀɴᴛ ᴄʜᴀʀᴀᴄᴛᴇʀꜱ. ᴇɴɢᴀɢᴇ ɪɴ ᴄʜᴀʟʟᴇɴɢᴇꜱ, ᴛʀᴀᴅᴇ ᴡɪᴛʜ ꜰᴇʟʟᴏᴡ ᴇɴᴛʜᴜꜱɪᴀꜱᴛꜱ, ᴀɴᴅ ʙᴜɪʟᴅ ʏᴏᴜʀ ᴜʟᴛɪᴍᴀᴛᴇ ᴀɴɪᴍᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ. ʟᴇᴛ'ꜱ ᴅɪᴠᴇ ɪɴᴛᴏ ᴛʜɪꜱ ᴀᴅᴠᴇɴᴛᴜʀᴇ ᴛᴏɢᴇᴛʜᴇʀ !***
        """
        keyboard = [
            [InlineKeyboardButton("+ Sᴛᴀʀᴛ Gʀᴀʙʙɪɴɢ +", url=f'http://t.me/CatchEmWaifuBot?startgroup=new')],
             [InlineKeyboardButton("🏥 Sᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{SUPPORT_CHAT}')],
            [InlineKeyboardButton("📘 Uᴘᴅᴀᴛᴇꜱ", url=f'https://t.me/{UPDATE_CHAT}')],
            [InlineKeyboardButton("⚙ Hᴇʟᴘ", callback_data='help')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$', block=False))
start_handler = CommandHandler('start', start, block=False)
application.add_handler(start_handler)
