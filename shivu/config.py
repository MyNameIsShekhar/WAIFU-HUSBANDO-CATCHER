class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "5054912509"
    sudo_users = "5054912509", "6758236533"
    GROUP_ID = -1002028197914
    TOKEN = "6399571286:AAGbicH18fW9vdszPn-4Yu0ELIGTx2Wl9Lc"
    mongo_url = "mongodb+srv://ixbotmongodb:RadheRadhe@cluster0.ga1q2fn.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = ["https://graph.org/file/1fa22a6a15c70105286aa.jpg", "https://graph.org/file/1fa22a6a15c70105286aa.jpg"]
    SUPPORT_CHAT = "Grab_Your_Characters_6"
    UPDATE_CHAT = "Grab_Your_Characters_6"
    BOT_USERNAME = "Grab_Your_Characters_ixbot"
    CHARA_CHANNEL_ID = "-1002031301319"
    api_id = 20967639
    api_hash = "f0cc55917e860f93d2c9aaa4a7caa69c"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
