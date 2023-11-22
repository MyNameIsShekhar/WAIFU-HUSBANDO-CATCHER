from telegram.ext import InlineQueryHandler,CallbackQueryHandler, ChosenInlineResultHandler, CallbackContext, Updater
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto
import asyncio
import time
from telegram import Update
from shivu import application 
from shivu import user_collection, collection

async def inlinequery(update: Update, context: CallbackContext) -> None:
    from collections import Counter

    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    if query.isdigit():
        user = await user_collection.find_one({'id': int(query)})

        if user:
            
            character_ids = [character['id'] for character in user['characters']]

            
            character_counts = Counter(character_ids)

            characters = list({v['id']:v for v in user['characters']}.values())[offset:offset+50]
            if len(characters) > 50:
                characters = characters[:50]
                next_offset = str(offset + 50)
            else:
                next_offset = str(offset + len(characters))

            results = []
            for character in characters:
                anime_characters_guessed = sum(c['anime'] == character['anime'] for c in user['characters'])
                total_anime_characters = await collection.count_documents({'anime': character['anime']})

                rarity = character.get('rarity', "Don't have rarity.. ")

                count = character_counts[character['id']]

                results.append(
                    InlineQueryResultPhoto(
                        thumbnail_url=character['img_url'],
                        id=f"{character['id']}_{time.time()}",
                        photo_url=character['img_url'],
                        caption=f"<b><a href='tg://user?id={user['id']}'>{user.get('first_name', user['id'])}</a>'s Character</b>\n\n🌸: <b>{character['name']} (x{count})</b>\n🏖️: <b>{character['anime']} ({anime_characters_guessed}/{total_anime_characters})</b>\n<b>{rarity}</b>\n\n🆔: <b>{character['id']}</b> ",
                        parse_mode='HTML'
                    )
                )

            await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)
        else:
            await update.inline_query.answer([InlineQueryResultArticle(
                id='notfound', 
                title="User not found", 
                input_message_content=InputTextMessageContent("User not found")
            )], cache_time=5)


application.add_handler(InlineQueryHandler(inlinequery, block=False))
