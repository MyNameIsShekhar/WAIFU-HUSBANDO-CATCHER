import re
import time
from html import escape

from telegram import Update, InlineQueryResultPhoto
from telegram.ext import InlineQueryHandler, CallbackContext, CommandHandler 
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

winter_img = "https://graph.org/file/7bfc05c5787aa19370dc8.jpg"

from shivu import user_collection, collection, application

async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    if query.startswith('collection.'):
        user_id, *search_terms = query.split(' ')[0].split('.')[1], ' '.join(query.split(' ')[1:])
        if user_id.isdigit():
            user = await user_collection.find_one({'id': int(user_id)})
            if user:
                all_characters = list({v['id']:v for v in user['characters']}.values())
                if search_terms:
                    regex = re.compile(' '.join(search_terms), re.IGNORECASE)
                    all_characters = [character for character in all_characters if regex.search(character['name']) or regex.search(character['anime'])]
            else:
                all_characters = []
        else:
            all_characters = []
    elif query.startswith('❄️_Winter'):
        search_terms = ' '.join(query.split(' ')[1:])
        all_characters = list(await collection.find({"rarity": "❄️ Winter"}).to_list(length=None))
        if search_terms:
            regex = re.compile(search_terms, re.IGNORECASE)
            all_characters = [character for character in all_characters if regex.search(character['name']) or regex.search(character['anime'])]
    else:
        if query:
            regex = re.compile(query, re.IGNORECASE)
            all_characters = list(await collection.find({"$or": [{"name": regex}, {"anime": regex}]}).to_list(length=None))
        else:
            all_characters = list(await collection.find({}).to_list(length=None))

    characters = all_characters[offset:offset+50]
    if len(characters) > 50:
        characters = characters[:50]
        next_offset = str(offset + 50)
    else:
        next_offset = str(offset + len(characters))

    results = []
    for character in characters:
        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})

        if query.startswith('collection.'):
            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])
            caption = f"<b> Look At <a href='tg://user?id={user['id']}'>{(escape(user.get('first_name', user['id'])))}</a>'s Character</b>\n\n🌸: <b>{character['name']} (x{user_character_count})</b>\n🏖️: <b>{character['anime']} ({user_anime_characters}/{anime_characters})</b>\n<b>{character['rarity']}</b>\n\n<b>🆔️:</b> {character['id']}"
        else:
            caption = f"<b>Look At This Character !!</b>\n\n🌸:<b> {character['name']}</b>\n🏖️: <b>{character['anime']}</b>\n<b>{character['rarity']}</b>\n🆔️: <b>{character['id']}</b>\n\n<b>Globally Guessed {global_count} Times...</b>"
        results.append(
            InlineQueryResultPhoto(
                thumbnail_url=character['img_url'],
                id=f"{character['id']}_{time.time()}",
                photo_url=character['img_url'],
                caption=caption,
                parse_mode='HTML'
            )
        )

    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

