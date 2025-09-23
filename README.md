# Library Service Project

---

## Table of Contents

- [Features](#features)  
- [Requirements](#requirements)  
- [Setup / Installation](#setup--installation)  
- [Usage](#usage)  
- [Testing & Load Testing](#testing--load-testing)  
- [Background Workers & Tools](#background-workers--tools)  
- [Non-Functional Constraints](#non-functional-constraints)  
- [Contributing](#contributing)  
- [License](#license)

---

## Features

- Inventory management (books)  
- Borrowing system (users can borrow, return books)  
- Customer/user accounts & authentication (JWT)  
- Payment integration (Stripe)  
- Notifications (Telegram)
- async tasks (Celery)
- Pagination on listings  
- Traffic / usage tracking (middleware & utilities)  

---

## Requirements

- Docker & Docker Compose  
- Python 3.10+ (if running locally)  
- PostgreSQL  
- Redis  
- Stripe API credentials for payment processing  
- Environment variables (see below)  

---

## Setup / Installation

> These instructions assume you are using Docker.  
> For local setup, you’ll need to install dependencies and configure PostgreSQL & Redis manually.

### 1. Clone the repository

```
git clone https://github.com/RomanSapunGit/library-service-project.git
cd library-service-project
git checkout develop
```

### 2. Create environment files

- `.env` — for local / non-Docker settings  
- `.env.docker` — for Docker Compose  

Fill in variables such as:

- `POSTGRES_USER`, 
- `POSTGRES_PASSWORD`, 
- `POSTGRES_DB`  
- `POSTGRES_HOST`, 
- `POSTGRES_DB_PORT` ,
- `REDIS_HOST`, 
- `STRIPE_API_KEY`,  
- `SECRET_KEY`,  
- `TELEGRAM_BOT_TOKEN`,
- `CHAT_ID`,
- `STRIPE_SECRET`,
- `CELERY_BROKER_URL`
- `SWAGGER_JSON`
- `NGROK_AUTHTOKEN`
---

### 3. Start services

```
docker-compose up --build
```
- db (PostgreSQL)

- redis

- library (Django app with Gunicorn)

- ngrok for app webhook to work

- celery worker

### 4. Run migrations and load initial data

```
docker-compose exec library python manage.py migrate
docker-compose exec library python manage.py loaddata library_data.json
```

### 5. Access the app
Firstly, you need to visit ngrok and get generated url
`http://localhost:4040`

Then access app via that url.

## Usage

- **Authentication** → `/api/users/tokens/` (JWT)  
- **Borrow a book** → POST `/api/borrowings/`  
- **Manage inventory** → `/api/books/`  
- **Payments** → Stripe checkout sessions  

For more information please refer to documentation:
```api/doc/swagger/```

Always include Authorize header in responses:
```Authorize: Bearer <token>```

---
## Testing & Load Testing

To run unit tests use:
```python manage.py test```

The project includes a [Locust](https://locust.io/) load test (`locustfile.py`).

Run:

```
locust -f locustfile.py --host=http://localhost:8000
```
Then open http://localhost:8089 , set number of users & spawn rate, provide the host, and click Start.
This allows you to check concurrency and system performance.

---
## Background Workers & Tools

### Celery Workers

Start Celery worker:

```
celery -A library_service worker --loglevel=INFO --pool=solo
```

Start Celery beat (for scheduled tasks):

```
celery -A library_service beat --loglevel=INFO
```

### Ngrok (for external tunneling)
Expose local service via ngrok:
```docker run -it -e NGROK_AUTHTOKEN=<your-token> ngrok/ngrok:latest http host.docker.internal:8000```

Replace <your-token> with your personal Ngrok authtoken.

---

## Non-Functional Constraints

The system is designed to support:

- Up to **5 concurrent users**  
- **1,000 books** in inventory  
- Up to **50,000 borrowings per year**  
- Total traffic ≤ **30 MB per year**  

> These constraints affect pagination, caching, and resource usage strategies.

---

## Contributing

We welcome contributions! To contribute:

1. Fork the repository  
2. Create a feature branch:  
   ```
   git checkout -b feature/your-feature
   ```
3. Make your changes and add tests
Commit your changes with clear messages

Push your branch and submit a Pull Request to `develop`.
Follow conventional commits for clear history, e.g., `feat: add new borrowing endpoint`.

## License

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
