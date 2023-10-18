import telegram.ext as tg

WORKERS = (
        8 # Number of subthreads to use. Set as number of threads your processor uses
)
TOKEN = "6420751168:AAEtf-OyEYLLTZM2c4LrhIroXPfvsW7KlM8"

updater = tg.Updater(
    token=TOKEN,
    workers=WORKERS,
    request_kwargs={"read_timeout": 10, "connect_timeout": 10},
    use_context=True,
)

dispatcher = updater.dispatcher
