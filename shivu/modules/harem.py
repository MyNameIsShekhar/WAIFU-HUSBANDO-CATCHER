from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters
from shivu import db, collection, user_totals_collection, user_collection, top_global_groups_collection, top_global_groups_collection, group_user_totals_collection, photo_urls

async def harem(update: Update, context: CallbackContext, page=0) -> None:
    user_id = update.effective_user.id

    user = await user_collection.find_one({'id': user_id})
    if not user:
        if update.message:
            await update.message.reply_text('You have not guessed any characters yet.')
        else:
            await update.callback_query.edit_message_text('You have not guessed any characters yet.')
        return

    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))

    # Group the characters by id and count the occurrences
    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}

    # Remove duplicates
    unique_characters = list({character['id']: character for character in characters}.values())

    # Calculate the total number of pages
    total_pages = math.ceil(len(unique_characters) / 15)  # Number of characters divided by 15 characters per page, rounded up

    # Check if page is within bounds
    if page < 0 or page >= total_pages:
        page = 0  # Reset to first page if out of bounds

    harem_message = f"<b>{update.effective_user.first_name}'s Harem - Page {page+1}/{total_pages}</b>\n"

    # Get the characters for the current page
    current_characters = unique_characters[page*15:(page+1)*15]

    # Group the current characters by anime
    current_grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

    for anime, characters in current_grouped_characters.items():
        harem_message += f'\n🏖️ <b>{anime} {len(characters)}/{await collection.count_documents({"anime": anime})}</b>\n'

        for character in characters:
            
            count = character_counts[character['id']]  # Get the count from the character_counts dictionary
            harem_message += f'{character["id"]} {character["name"]} ×{count}\n'

         # Add a line break after each anime group

    total_count = len(user['characters'])
    
    keyboard = [[InlineKeyboardButton(f"See All Characters ({total_count})", switch_inline_query_current_chat=str(user_id))]]

    # Add navigation buttons if there are multiple pages
    if total_pages > 1:
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"harem:{page-1}:{user_id}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"harem:{page+1}:{user_id}"))
        keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    if 'favorites' in user and user['favorites']:
        # Get the favorite character
        fav_character_id = user['favorites'][0]
        fav_character = next((c for c in user['characters'] if c['id'] == fav_character_id), None)

        if fav_character and 'img_url' in fav_character:
            if update.message:
                await update.message.reply_photo(photo=fav_character['img_url'], parse_mode='HTML', caption=harem_message, reply_markup=reply_markup)
            else:
                # Check if the new caption is different from the existing one
                if update.callback_query.message.caption != harem_message:
                    await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup, parse_mode='HTML')
        else:
            if update.message:
                await update.message.reply_text(harem_message, parse_mode='HTML', reply_markup=reply_markup)
            else:
                # Check if the new text is different from the existing one
                if update.callback_query.message.text != harem_message:
                    await update.callback_query.edit_message_text(harem_message, parse_mode='HTML', reply_markup=reply_markup)
    else:
        # Check if the user's collection is not empty
        if user['characters']:
            # Get a random character from the user's collection
            random_character = random.choice(user['characters'])

            if 'img_url' in random_character:
                if update.message:
                    await update.message.reply_photo(photo=random_character['img_url'], parse_mode='HTML', caption=harem_message, reply_markup=reply_markup)
                else:
                    # Check if the new caption is different from the existing one
                    if update.callback_query.message.caption != harem_message:
                        await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup, parse_mode='HTML')
            else:
                if update.message:
                    await update.message.reply_text(harem_message, parse_mode='HTML', reply_markup=reply_markup)
                else:
                    # Check if the new text is different from the existing one
                    if update.callback_query.message.text != harem_message:
                        await update.callback_query.edit_message_text(harem_message, parse_mode='HTML', reply_markup=reply_markup)
        else:
            if update.message:
                await update.message.reply_text("Your list is empty.")


async def harem_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data


    _, page, user_id = data.split(':')

    
    page = int(page)
    user_id = int(user_id)

    # Check if the user who clicked the button is the same as the user who owns the collection
    if query.from_user.id != user_id:
        await query.answer("Don't Stalk Other User's Harem.. lmao", show_alert=True)
        return

    
    await harem(update, context, page)


application.add_handler(CommandHandler("collection", harem,block=False))
harem_handler = CallbackQueryHandler(harem_callback, pattern='^harem')
application.add_handler(harem_handler)
    
