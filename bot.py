from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def draw_circle(draw: ImageDraw.Draw, coordinates: tuple[int, int], radius: int, fill: str):
    upper_left = (coordinates[0]-radius, coordinates[1]-radius)
    lower_right = (coordinates[0]+radius, coordinates[1]+radius)
    two_boxes = [upper_left, lower_right]
    draw.ellipse(two_boxes, fill=fill)

def welcome(update: Update, context: CallbackContext) -> None:
    for member in update.message.new_chat_members:
        user_id = member.id
        first_name = member.first_name

        # Get profile photo
        photos = context.bot.get_user_profile_photos(user_id).photos
        if photos:
            photo = photos[0][-1].get_file().download_as_bytearray()
            profile_pic = Image.open(BytesIO(photo))

            # Open the welcome image and draw the profile picture and text
            image = Image.open('assets/IMG_20231010_185349_978.jpg')
            draw = ImageDraw.Draw(image)

            # Draw profile picture in a circle on the left side of the image
            max_size = min(image.width, image.height) // 2  # Make the profile picture 50% of the image size
            profile_pic.thumbnail((max_size, max_size))
            circle_image = Image.new('L', profile_pic.size)
            circle_draw = ImageDraw.Draw(circle_image)
            draw_circle(circle_draw, (profile_pic.width // 2, profile_pic.height // 2), profile_pic.width // 2, 'white')
            profile_pic.putalpha(circle_image)
            image.paste(profile_pic, (10, image.height // 2 - profile_pic.height // 2))  # Position the profile picture on the left side

            # Write user's first name and user id below the profile picture
            font_size = max_size // 10  # Adjust size as needed
            font = ImageFont.truetype('assets/adrip1.ttf', font_size)
            text = f'{first_name}\nID: {user_id}'
            text_width, text_height = draw.textsize(text, font=font)
            draw.text((10 + max_size + 10, image.height // 2 - text_height // 2), text, fill='black', font=font)  # Position the text to the right of the profile picture

            # Send the modified welcome image
            byte_arr = BytesIO()
            image.save(byte_arr, format='PNG')
            byte_arr.seek(0)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=byte_arr)

def main() -> None:
    updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))

    updater.start_polling()

    updater.idle()
