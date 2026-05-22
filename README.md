# Book Store API
temp 2

A RESTful API built with **FastAPI** and **PostgreSQL** for managing a bookstore's operations. 
This system handles secure JWT-based user authentication, inventory management (books and authors), 
and comprehensive order processing with role-based access control (Admin and User).


## Key Features


- **User Authentication & Authorization:** Secure login and registration using JWT with distinct roles (`admin`, `user`).
- **Inventory Management:** Full CRUD operations for Books and Authors.
- **Order Processing:** Users can place and track orders, selecting delivery types (`standard`, `express`, `urgent`). 
- **Advanced Admin Capabilities:** Admins can manage users, update order statuses 
(`pending`, `paid`, `shipped`, `delivered`, `cancelled`), and export order data to `.xlsx`.
- **Powerful Filtering & Pagination:** The admin order endpoints support complex querying 
(e.g., filtering by total amount, priority, delivery type, status) and ordering.
- **Redis Caching:** Improved performance usings cache for GET books and authors lists.
- **Comprehensive Testing:** Full test coverage with pytest.


## Live Demo


**Base URL:** https://opvlad.dev

Try the API immediately:
- **Interactive docs:** https://opvlad.dev/docs
- **Health Check:** https://opvlad.dev/health


## Architecture


### Technology Stack

- **Python 3.12**
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Authentication:** JWT
- **Validation:** Pydantic
- **Caching:** Redis
- **Testing:** pytest

### Project Structure

```
book-store-api/
├── app/
│   ├── routers/v1/       # API endpoints (versioned)
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── books.py      # Book management
│   │   ├── authors.py    # Author management
│   │   ├── orders.py     # Order processing
│   │   └── users.py      # User management
│   ├── config/           # Setting for project and logging setup
│   ├── handlers/         # Event and exceptions handlers
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic validation schemas
│   ├── crud.py           # Database operations
│   ├── services.py       # Business logic layer
│   ├── security.py       # Auth and encryption utilities
│   ├── event_bus.py      # Event-driven architecture for cache invalidation
│   ├── database.py       # Database connection
│   ├── dependencies.py   # Dependency injection
│   └── main.py           # Application entry point
├── alembic/              # Database migrations
├── tests/                # Test suite
```


## Quick Start


### Option 1: Docker (recommended)
#### Prerequisites:
- Docker

```bash
# clone the repository
git clone https://github.com/opvlad/book-store-api.git
cd book-store-api

# create .env file
cp .env.example .env

# start containers
docker compose up --build
```
API will be available at: http://localhost:8000

Swagger UI: http://localhost:8000/docs


### Option 2: Local Setup
#### Prerequisites:
- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- uv 0.10.12+

```bash
# create virtual environment
python -m venv .venv
source .venv/bin/activate # Linux/Mac
.venv\Scripts\activate    # Windows

# install dependencies
uv sync

# create .env file
cp .env.example .env
# edit .env, specified DATABASE_URL and REDIS_URL

# run migrations
alembic upgrade head

# run server
uvicorn app.main:app --host localhost --port 8000
```


## API Endpoints


### Authentication
| Method | Endpoint             | Description        | Access |
|--------|----------------------|--------------------|--------|
| POST   | api/v1/auth/register | User registration  | All    |
| POST   | api/v1/auth/login    | Log in (get JWT)   | All    |

### Books
| Method | Endpoint           | Description      | Access |
|--------|--------------------|------------------|--------|
| GET    | /api/v1/books      | List all books   | All    |
| GET    | /api/v1/books/{id} | Get book details | All    |
| POST   | /api/v1/books      | Create a book    | Admin  |
| PATCH  | /api/v1/books/{id} | Update book      | Admin  |
| DELETE | /api/v1/books/{id} | Delete book      | Admin  |

### Authors
| Method | Endpoint             | Description         | Access |
|--------|----------------------|---------------------|--------|
| GET    | /api/v1/authors      | List all authors    | All    |
| GET    | /api/v1/authors/{id} | Get authors details | All    |
| POST   | /api/v1/authors      | Create author       | Admin  |
| PATCH  | /api/v1/authors/{id} | Update author       | Admin  |
| DELETE | /api/v1/authors/{id} | Delete author       | Admin  |

### Orders
| Method | Endpoint                   | Description                    | Access     |
|--------|----------------------------|--------------------------------|------------|
| GET    | /api/v1/orders/me          | List my orders                 | Authorized |
| GET    | /api/v1/orders/me/{id}     | Get my order details           | Authorized |
| POST   | /api/v1/orders             | Place an order                 | Authorized |
| GET    | /api/v1/orders             | List of all orders (filtering) | Admin      |
| GET    | /api/v1/orders/{id}        | Get order details              | Admin      |
| PATCH  | /api/v1/orders/{id}        | Change order status            | Admin      |
| DELETE | /api/v1/orders/{id}        | Delete order                   | Admin      |
| GET    | /api/v1/orders/export/xlsx | Export orders in .xlsx         | Admin      |

### Users
| Method | Endpoint          | Description                 | Access     |
|--------|-------------------|-----------------------------|------------|
| GET    | api/v1/users/me   | Read my profile             | Authorized |
| PATCH  | api/v1/users/me   | Change my username or email | Authorized |
| GET    | api/v1/users      | List of all users           | Admin      |
| GET    | api/v1/users/{id} | Get user details            | Admin      |
| PATCH  | api/v1/users/{id} | Change user status          | Admin      |
| DELETE | api/v1/users/{id} | Delete user                 | Admin      |


## Usage Example


### Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "email": "user1@example.com",
    "password": "secret"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@example.com",
    "password": "secret"
  }'
```

### Get List Books

```bash
curl "http://localhost:8000/api/v1/books?offset=0&limit=10"
```

### Place an Order

```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "items": [
      {"book_id": 1, "quantity": 2},
      {"book_id": 3, "quantity": 1}
    ]
  }'
```

## Testing


```bash
# run all tests
pytest -v

# run specific test file
pytest -v tests/test_books.py
```



## Environment Variables


| Variable                    | Description              | Default                                                         |
|-----------------------------|--------------------------|-----------------------------------------------------------------|
| DATABASE_URL                | Url for local PostgreSQL | postgresql+asyncpg://postgres:postgres@localhost:5432/bookstore |
| REDIS_URL                   | Url for local Redis      | redis://localhost:6379                                          |
| SECRET_KEY                  | Secret key for JWT       | my-long-secret-key-change-this-later                            |
| ACCESS_TOKEN_EXPIRE_MINUTES | Lifetime of token        | 30                                                              |
| ALGORITHM                   | Alghoritm for JWT        | HS256                                                           |


## Migrations


```bash
# create new migration
alembic alembic revision --autogenerate -m "description"

# apply migrations
alembic upgrade head

# rollback the last migration
alembic downgrade -1
```
