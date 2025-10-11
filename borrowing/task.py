from celery import shared_task
from django.utils import timezone

from telegram import Bot
import asyncio

from library_service import settings

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
CHAT_ID = settings.CHAT_ID


@shared_task
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


@shared_task
def send_borrowing_overdue_telegram_messages():
    from borrowing.models import Borrowing

    borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True,
        expected_return_date__lte=timezone.localdate()
    ).select_related("book")

    if len(borrowings) == 0:
        send_telegram_message(["No borrowing overdue today!"])
    else:
        for borrowing in borrowings:
            send_telegram_message([
                f"Borrowing with id {borrowing.id} for "
                f"book {borrowing.book} is overdue,"
                f"expected {borrowing.expected_return_date}",
                f"but today is {timezone.localdate()}"
            ])
