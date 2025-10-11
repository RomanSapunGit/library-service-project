from datetime import date, datetime

import redis
from django.http import JsonResponse

from library_service import settings

r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)
MAX_BYTES_PER_YEAR = 30 * 1024 * 1024

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

class TrafficLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        year = date.today().year
        key = f"traffic:{year}"
        size = len(response.content)

        new_total = r.incrby(key, size)
        r.expireat(key, datetime(year + 1, 1, 1))

        if new_total > MAX_BYTES_PER_YEAR:
            r.decrby(key, size)
            return JsonResponse(
                {"error": "Yearly traffic limit reached (30 MB)"},
                status=429
            )

        return response
