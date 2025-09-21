from telegram import Bot
import asyncio

from library_service import settings

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
CHAT_ID = settings.CHAT_ID


def send_telegram_message(messages):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    async def send_message(text, chat_id):
        async with bot:
            await bot.send_message(text=text, chat_id=chat_id)

    async def run_bot(messages, chat_id):
        text = '\n'.join(messages)
        await send_message(text, chat_id)

    if messages:
        asyncio.run(run_bot(messages, CHAT_ID))
