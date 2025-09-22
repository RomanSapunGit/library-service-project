import json

from datetime import datetime, timedelta, date
from locust import HttpUser, task

class LibraryUser(HttpUser):

    def on_start(self):
        response = self.client.post(
            "/api/users/tokens/",
            data=json.dumps({
                "email": "user@user.com",
                "password": "pass123"
            }),
            headers={"Content-Type": "application/json"}
        )
        print(response.status_code, response.text)
        self.token = response.json().get("access")

    @task
    def list_borrowings(self):
        payload = {
            "book": 1,
            "expected_return_date": (date.today() + timedelta(days=7)).isoformat()
        }

        self.client.post(
            "/api/borrowings/",
            payload,
            headers={"Authorize": f"Bearer {self.token}"}
        )
