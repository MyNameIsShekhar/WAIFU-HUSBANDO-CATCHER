class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "6988388558"
    sudo_users = "6988388558"
    GROUP_ID = -1001923606558
    TOKEN = "6326325208:AAHwvkozHtqq3fMz5WK8L-tXW6zSBVvKPUI
"
    mongo_url = "mongodb+srv://Erichdaniken:<Erichdaniken>@cluster0.o7kqnip.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = ["https://telegra.ph/file/b8608526465844c69d33b.jpg", "https://telegra.ph/file/aa31eea7cccaf81de0f66.jpg"]
    SUPPORT_CHAT = "hunter_dracoo_support"
    UPDATE_CHAT = "hunter_dracoo_support"
    BOT_USERNAME = "hunter_dracoo_bot"
    CHARA_CHANNEL_ID = "-1001923606558"
    api_id = 21592757
    api_hash = "43b8f1af3efcfe39f0cb1819efc64d64"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
