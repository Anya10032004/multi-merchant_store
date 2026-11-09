# REST API mini project: Multi-merchant store 🏬

Flask project that builds a multi-merchant store REST API. It demonstrates user authentication with JWT, role-based access control, store and product management (CRUD), product claiming, database relationships using Flask-SQLAlchemy, and catalog features such as search, filtering, and pagination.

## 💻 System Requirement
 - Python 3.14.3(make sure to click the "Add Python to PATH" button befor download)
 - MySQL Database Server(you can use XAMPP or Laragon, but i use Laragon)
 - Postman(for API testing)
 - Vs code(Code editor) or you can also use Antigravity IDE(make sure the antigravity that you are download has a black background)

## ⚙️ Project structure 

```
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── errors.py
|   |── extensions.py
│   └── routes/
│       ├── auth.py
│       ├── merchants.py
│       ├── products.py
│       ├── catalog.py
│       └── claims.py
├── requirements.txt
└── run.py
```
## 🗄 Database Configuration
1. Start Laragon. After installing Laragon, open the Laragon Control Panel and click Start All to start the required services.
2. Open phpMyAdmin. In the Laragon Control Panel, click Menu, select MySQL, and then click phpMyAdmin.
3. Log in to phpMyAdmin. Your browser will open the phpMyAdmin login page. By default, Laragon uses the following credentials:
    - Username: root(your username, but i use teh default which is root)
    - Password: no password(your password, but by default we dont need password)
4. Enter root as the username and password( or just let it blank), and click Log in.
5. When you finally login to the phpMyAdmin page, you will see this page:
   <img src="images/laragon.png" alt="Laragon Control Panel" width="600">
7. In the navigation bar above, pick the "SQL" button, and it will lead you to the SQL Query Editor

    <img src="images/navigation_bar.png" alt="navigation_bar" width="600">
    
    <img src="images/sql_button.png" alt="sql_button" width="600">
    
    <img src="images/SQLQueryEditor.png" alt="SQLQueryEditor" width="600">
8.In the the SQL Query Editor Create the database name "perpustakaan" with the following Query:

     CREATE DATABASE perpustakaan;
    

## 2. Setup

Use Python 3.14.3 or newer
```bash
python -m venv .venv
```

Activate the environment:

**Windows**
```bash
.venv\\Scripts\\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then set `DATABASE_URL`.

For MySQL, create the database first:

```sql
CREATE DATABASE db_store;
```

Example MySQL URL:

```text
mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/db_store
```

For a quick local experiment without MySQL, use:

```text
sqlite:///store.db
```

`run.py` loads the `.env` file using `python-dotenv` before creating the app.

## 3. Run the API

```bash
python run.py
```

The development server runs at `http://127.0.0.1:5000`.

The example calls `db.create_all()` when run directly so you can start learning without a migration setup. For a production project, use Flask-Migrate/Alembic instead of relying on `create_all()` to evolve your schema.

## 4. API endpoint overview

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/api` | Public | Health check |
| POST | `/api/register` | Public | Register a user or merchant |
| POST | `/api/login` | Public | Login and receive a JWT |
| POST | `/api/merchants` | Merchant | Create merchant profile |
| GET | `/api/merchant/me` | Merchant | Get own merchant profile |
| PUT | `/api/merchant/me` | Merchant | Update own merchant profile |
| GET | `/api/merchants` | Merchant | List merchant profiles |
| GET | `/api/merchants/<id>` | Authenticated | Get merchant and its products |
| POST | `/api/products` | Merchant | Create a product |
| GET | `/api/products/mine` | Merchant | List own products |
| PUT | `/api/products/<id>` | Merchant | Update own product |
| DELETE | `/api/products/<id>` | Merchant | Delete own product |
| GET | `/api/catalog` | Public | Browse/search available products |
| GET | `/api/catalog/<id>` | Public | Get one catalog product |
| POST | `/api/claims` | User | Claim a product and reduce stock |
| GET | `/api/claims` | User | List own claims |

For protected endpoints, send the token in the request header:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 5. Example request bodies

Register:

```json
{
  "name": "Anya",
  "email": "anya@example.com",
  "password": "example-password",
  "role": "merchant"
}
```

Create merchant profile:

```json
{
  "store_name": "Anya Store",
  "description": "A small online store",
  "address": "South Tangerang",
  "phone": "08123456789"
}
```

Create product:

```json
{
  "name": "Laptop",
  "description": "A sample laptop",
  "price": 12000000,
  "stock": 5
}
```

Claim a product as a user:

```json
{
  "product_id": 1,
  "quantity": 2
}
```

Catalog filters:

```text
GET /api/catalog?search=laptop&merchant_id=1&page=1&per_page=10
```

## 6. How the architecture works

- `run.py`: creates the app and starts the development server.
- `app/__init__.py`: contains `create_app()`, initializes extensions, and registers Blueprints.
- `config.py`: stores settings such as the database URL and JWT secret.
- `models.py`: defines database tables and serialization methods.
- `errors.py`: centralizes HTTP and unexpected error responses.
- `routes/`: contains endpoint functions grouped by feature.
- `routes/helpers.py`: contains shared route helpers, including role authorization.

### Request flow

```text
Client / Postman
      |
      v
Route Blueprint
      |
      v
JWT authentication (if protected)
      |
      v
Role authorization (if required)
      |
      v
SQLAlchemy model / database
      |
      v
JSON response
```

## 7. Important learning notes

1. A Blueprint groups related endpoints. It does not create a separate Flask application.
2. The application factory lets you configure and initialize the app in one place.
3. `db` is initialized once in `app/__init__.py`, then imported where database access is needed.
4. `@jwt_required()` verifies the access token. `@role_required("merchant")` checks the role claim after authentication.
5. `get_jwt_identity()` returns the identity stored in the token. This project stores the user ID as a string.
6. Passwords are hashed before storage. The password hash is never returned in API responses or included in JWT claims.
7. A merchant can only update or delete products belonging to that merchant.
8. A claim reduces stock and creates a claim record in the same database transaction.

This is a teaching reference, not a production-hardened service. Before production, add database migrations, stronger input validation, rate limiting, tests, HTTPS, secure secret management, and transaction/concurrency handling for stock updates.
