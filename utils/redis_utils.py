from datetime import date

import redis

from library_service import settings

r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)

def increment_borrowing_counter():
    year = date.today().year
    new_value = r.hincrby("borrowings", str(year), 1)
    if new_value > 50_000:
        r.hincrby("borrowings", str(year), -1)
        raise Exception("Yearly borrowing limit reached")

MAX_BOOKS = 1000
COUNTER_KEY = "books_count"

def create_book(inventory):
    new_value = r.incrby(COUNTER_KEY, inventory)
    if new_value > MAX_BOOKS:
        r.decrby(COUNTER_KEY, inventory)
        raise Exception("Maximum number of books reached")


def delete_book(inventory):
    r.decrby(COUNTER_KEY, inventory)
