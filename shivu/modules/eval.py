#credit @ishikki_Akabane

import io
import os
import textwrap
import traceback
from contextlib import redirect_stdout

from shivu import application, LOGGER
from telegram import Update
from telegram.constants import ChatID, ParseMode
from telegram.ext import ContextTypes, CommandHandler
from telegram.ext import CallbackContext 

namespaces = {}
DEV_LIST = [6404226395]

def namespace_of(chat, update, bot):
    if chat not in namespaces:
        namespaces[chat] = {
            "__builtins__": globals()["__builtins__"],
            "bot": bot,
            "effective_message": update.effective_message,
            "effective_user": update.effective_user,
            "effective_chat": update.effective_chat,
            "update": update,
        }

    return namespaces[chat]


def log_input(update):
    user = update.effective_user.id
    chat = update.effective_chat.id
    LOGGER.info(f"IN: {update.effective_message.text} (user={user}, chat={chat})")


async def send(msg, bot, update):
    if len(str(msg)) > 2000:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "output.txt"
            await bot.send_document(
                chat_id=update.effective_chat.id, 
                document=out_file, 
                message_thread_id=update.effective_message.message_thread_id if update.effective_chat.is_forum else None
            )
    else:
        LOGGER.info(f"OUT: '{msg}'")
        await bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"`{msg}`",
            parse_mode=ParseMode.MARKDOWN,
            message_thread_id=update.effective_message.message_thread_id if update.effective_chat.is_forum else None
        )


async def evaluate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message.from_user.id not in DEV_LIST:
        return

    bot = context.bot
    await send(await do(eval, bot, update), bot, update)


async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message.from_user.id not in DEV_LIST:
        return

    bot = context.bot
    await send(await do(exec, bot, update), bot, update)


def cleanup_code(code):
    if code.startswith("```") and code.endswith("```"):
        return "\n".join(code.split("\n")[1:-1])
    return code.strip("` \n")


async def do(func, bot, update):
    log_input(update)
    content = update.message.text.split(" ", 1)[-1]
    body = cleanup_code(content)
    env = namespace_of(update.message.chat_id, update, bot)

    os.chdir(os.getcwd())
    with open(
        "temp.txt", "w",
    ) as temp:
        temp.write(body)

    stdout = io.StringIO()

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    try:
        exec(to_compile, env)
    except Exception as e:
        return f"{e.__class__.__name__}: {e}"

    func = env["func"]

    try:
        with redirect_stdout(stdout):
            func_return = await func()
    except Exception as e:
        value = stdout.getvalue()
        return f"{value}{traceback.format_exc()}"
    else:
        value = stdout.getvalue()
        result = None
        if func_return is None:
            if value:
                result = f"{value}"
            else:
                try:
                    result = f"{repr(eval(body, env))}"
                except:
                    pass
        else:
            result = f"{value}{func_return}"
        if result:
            return result


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message.from_user.id not in DEV_LIST:
        return

    bot = context.bot
    log_input(update)
    global namespaces
    if update.message.chat_id in namespaces:
        del namespaces[update.message.chat_id]
    await send("Cleared locals.", bot, update)


EVAL_HANDLER = CommandHandler(("e", "ev", "eva", "eval"), evaluate, block=False)
EXEC_HANDLER = CommandHandler(("x", "ex", "exe", "exec", "py"), execute, block=False)
CLEAR_HANDLER = CommandHandler("clearlocals", clear, block=False)

application.add_handler(EVAL_HANDLER)
application.add_handler(EXEC_HANDLER)
application.add_handler(CLEAR_HANDLER)
