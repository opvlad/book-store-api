# 📚 Book Store API

A RESTful API built with **FastAPI** and **PostgreSQL** for managing a bookstore's operations. 
This system handles secure JWT-based user authentication, inventory management (books and authors), 
and comprehensive order processing with role-based access control (Admin vs. User).

## ✨ Features

* **User Authentication & Authorization:** Secure login and registration using JWT with distinct roles (`admin`, `user`).
* **Inventory Management:** Full CRUD operations for Books and Authors, including real-time stock quantity tracking.
* **Order Processing:** Users can place and track orders, selecting delivery types (`standard`, `express`, `urgent`). 
* **Advanced Admin Capabilities:** Admins can manage users, update order statuses (`pending`, `paid`, `shipped`, `delivered`, `cancelled`), and export order data to `.xlsx`.
* **Powerful Filtering & Pagination:** The admin order endpoints support complex querying (e.g., filtering by total amount, priority, delivery type, status) and ordering.
* **Health Checks:** Built-in health monitoring endpoint.

---

## 🚀 Getting Started

### Prerequisites
* **Python:** 3.8+
* **Database:** PostgreSQL installed and running locally or remotely.
* **Git:** Installed on your machine.

### ⚙️ Environment Variables

Create a `.env` file in the root directory of your project and configure the following required variables:

```env
# Database Configuration
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database_name>

# Security & JWT Auth
SECRET_KEY=your_super_secret_random_string_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30