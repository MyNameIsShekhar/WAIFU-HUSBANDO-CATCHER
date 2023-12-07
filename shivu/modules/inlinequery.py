from pyrogram import Client, filters, types, enums 
import asyncio
import time
import re
from collections import Counter
from shivu import shivuu
from shivu import user_collection, collection



@shivuu.on_inline_query()
async def inlinequery(client: Client, query: types.InlineQuery):
    offset = int(query.offset) if query.offset else 0

    if query.query.startswith('collection.'):
        user_id, *search_terms = query.query.split(' ')[0].split('.')[1], ' '.join(query.query.split(' ')[1:])
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
    else:
        if query.query:
            regex = re.compile(query.query, re.IGNORECASE)
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

        if query.query.startswith('collection.'):
            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])
            caption = f"<b> Look At <a href='tg://user?id={user['id']}'>{user.get('first_name', user['id'])}</a>'s Character</b>\n\n🌸: <b>{character['name']} (x{user_character_count})</b>\n🏖️: <b>{character['anime']} ({user_anime_characters}/{anime_characters})</b>\n<b>{character['rarity']}</b>\n\n<b>🆔️:</b> {character['id']}"
        else:
            caption = f"<b>Look At This Character !!</b>\n\n🌸:<b> {character['name']}</b>\n🏖️: <b>{character['anime']}</b>\n<b>{character['rarity']}</b>\n🆔️: <b>{character['id']}</b>\n\n<b>Globalllly Guessed {global_count} Times...</b>"
        results.append(
            types.InlineQueryResultPhoto(
                thumb_url=character['img_url'],
                id=f"{character['id']}_{time.time()}",
                photo_url=character['img_url'],
                caption=caption,
                parse_mode=enums.ParseMode.HTML
            )
        )

    await client.answer_inline_query(query.id, results, next_offset=next_offset, cache_time=5, is_gallery=True)


