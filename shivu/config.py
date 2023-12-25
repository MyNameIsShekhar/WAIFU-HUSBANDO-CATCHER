class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "6765826972"
    sudo_users = "6845325416", "6765826972"
    GROUP_ID = -1002133191051
    TOKEN = "6653243642:AAEaI93MNElP8WXsQ59AZWZgvnZ1WpnVTyY"
    mongo_url = "mongodb+srv://ixbotmongodb:RadheRadhe@cluster0.ga1q2fn.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = ["https://telegra.ph/file/b5b4b464581fc56c2a690.jpg", "https://telegra.ph/file/60f16b14f097252e4b412.jpg"]
    SUPPORT_CHAT = "Grab_Your_Characters_6"
    UPDATE_CHAT = "Grab_Your_Characters_6"
    BOT_USERNAME = "Grab_Your_Husbando_IxBot"
    CHARA_CHANNEL_ID = "-1001873432374"
    api_id = 20967639
    api_hash = "f0cc55917e860f93d2c9aaa4a7caa69c"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
