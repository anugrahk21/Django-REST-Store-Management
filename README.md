# Django-REST-Store-Management 🛒

## 📋 Project Overview

This repository hosts **Django-REST-Store-Management** — a full-stack store management system built with **Django** and **Django REST Framework (DRF)**. It features a complete **template-based frontend** for customers and admins, alongside a **RESTful API** for programmatic access to inventory data.

### ✨ What It Does

- **Customer Storefront** — Browse products and place orders directly from the web interface.
- **Admin Dashboard** — Manage inventory, track stock levels, and view revenue analytics.
- **REST API** — Programmatic CRUD access to products with advanced filtering.
- **Point of Sale (POS)** — Order creation with automatic stock deduction and transaction safety.

---

## 📚 Key Learnings & Concepts Implemented

This project was built step-by-step, incorporating the following core Django & REST API concepts:

### 1. 🏗️ Project Structure & Setup

- **Project vs. App:**
  - `storemanagement/`: The configuration root (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`).
  - `app/`: The business logic layer (`models`, `views`, `serializers`, `forms`, `urls`).
- **Environment:** Used `venv` for dependency isolation.
- **Commands used:**

```bash
django-admin startproject storemanagement .  # Start project in current dir
python manage.py startapp app                # Create the app
```

### 2. 🗃️ Database & Models

Four interconnected models power the system:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| **`Category`** | Product categorization | `name` |
| **`Product`** | Inventory items | `name`, `description`, `price`, `stock`, `category` (FK) |
| **`Order`** | Customer purchases | `user` (FK → User), `total_amount`, timestamps |
| **`OrderItem`** | Line items in an order | `order` (FK), `product` (FK), `quantity`, `price_at_time_of_order` |

- **Relationships:** `Product → Category` (ForeignKey), `Order → User` (ForeignKey), `OrderItem → Order & Product` (ForeignKeys).
- **Computed Fields:** `OrderItem.line_total()` calculates `quantity × price_at_time_of_order`.
- **Migrations:**
  - `makemigrations`: Prepares the blueprint for DB changes.
  - `migrate`: Applies changes to the actual `db.sqlite3` file.
- **Learning:** Adding a non-nullable field to existing data requires a default value to fix migration errors.

### 3. 🚀 Django REST Framework (DRF)

- **Serializers:** The bridge between complex database objects and JSON.
  - Used `ModelSerializer` to automatically map `Product` model to JSON.
  - Added `category_name` as a read-only field using `source='category.name'`.
- **ViewSets:**
  - `ModelViewSet` provided instant CRUD (Create, Read, Update, Delete) without writing manual views.
- **Routers:**
  - `DefaultRouter` automatically generated URLs for the ViewSet (`/api/products/`).

### 4. 🔐 Authentication (Session-Based)

Implemented **Django's built-in session authentication** for the admin dashboard.

- **How It Works:**
  1. Admin navigates to `/login/` → presented with Django's `AuthenticationForm`.
  2. On valid submission, `login()` creates a session → redirect to `/dashboard/`.
  3. Only **staff users** (`is_staff=True`) can access the dashboard.
  4. `logout()` destroys the session → redirect to home page.
- **Access Control:**
  - Custom `admin_required` decorator combines `@login_required` + `@user_passes_test(is_staff)`.
  - All dashboard views (inventory, product CRUD, revenue) are protected.
- **Guest Orders:** Unauthenticated customers can still place orders — a `guest_customer` user is auto-created.

### 5. 🔍 Custom Filtering (API)

Implemented `get_queryset` override on the `ProductViewSet` to filter data dynamically:

| Parameter    | Example                              | Description            |
|-------------|---------------------------------------|------------------------|
| `name`      | `?name=Laptop`                        | Search by product name |
| `category`  | `?category=electronics`               | Filter by category     |
| `min_price` | `?min_price=100`                      | Minimum price filter   |
| `max_price` | `?max_price=500`                      | Maximum price filter   |
| `in_stock`  | `?in_stock=true`                      | Only in-stock products |

- **Combinable:** All filters can be chained: `?category=electronics&min_price=100&in_stock=true`

### 6. 🛒 Point of Sale (POS) & Orders

- **Order Flow:**
  1. Customer adds products to cart on the home page.
  2. `POST /order/` with JSON payload `{"items": [{"id": 1, "quantity": 2}]}`.
  3. Backend validates stock availability, calculates totals, and creates the order atomically.
  4. Stock is automatically deducted using `transaction.atomic()` for data integrity.
- **Edge Cases Handled:**
  - Duplicate product IDs in cart are normalized (quantities merged).
  - Insufficient stock returns a descriptive error.
  - Invalid/empty carts are rejected gracefully.

### 7. 📊 Revenue & Analytics

- **Revenue Dashboard** (`/revenue/`): Displays all orders with line items, customer info, and total revenue.
- **Dashboard Stats:** Product count, low-stock alerts (< 10 units), and total revenue summary.

### 8. 🎨 Frontend (Template-Based)

| Template                     | Purpose                                   |
|-----------------------------|-------------------------------------------|
| `base.html`                 | Customer-facing base layout               |
| `admin_base.html`           | Admin dashboard base layout               |
| `home.html`                 | Product catalog & shopping cart            |
| `login.html`                | Admin login form                          |
| `dashboard.html`            | Inventory management with search          |
| `product_form.html`         | Add / Edit product form                   |
| `product_confirm_delete.html`| Delete confirmation page                 |
| `revenue.html`              | Revenue analytics & order history         |

- **Dark Theme:** Custom CSS in `static/css/style.css`.
- **Responsive:** Form controls use Bootstrap-compatible classes (`form-control`, `form-select`).

---

## 🛠️ Tech Stack

| Layer      | Technology                              |
|-----------|------------------------------------------|
| Language  | Python 3.11+                             |
| Framework | Django 5.2                               |
| API       | Django REST Framework (DRF)              |
| Auth      | Django built-in session authentication   |
| Database  | SQLite (`db.sqlite3`)                    |
| Frontend  | Django Templates + CSS                   |
| Admin     | Django Admin (customized with inlines)   |

---

## 📁 Project Structure

```
PEP_CAPSTONE/
├── storemanagement/              # Django project root
│   ├── storemanagement/          # Project configuration
│   │   ├── settings.py           # Django settings
│   │   ├── urls.py               # Root URL routing (admin, app, API)
│   │   ├── wsgi.py               # WSGI entry point
│   │   └── asgi.py               # ASGI entry point
│   ├── app/                      # Main application
│   │   ├── models.py             # Category, Product, Order, OrderItem
│   │   ├── views.py              # All views (HTML + API ViewSet)
│   │   ├── serializers.py        # DRF ProductSerializer
│   │   ├── forms.py              # ProductForm (ModelForm)
│   │   ├── urls.py               # App-level URL patterns
│   │   └── admin.py              # Admin customization + inlines
│   ├── templates/                # HTML templates
│   │   ├── base.html             # Customer base layout
│   │   ├── admin_base.html       # Admin base layout
│   │   ├── home.html             # Storefront
│   │   ├── dashboard.html        # Inventory management
│   │   ├── revenue.html          # Revenue analytics
│   │   └── ...                   # Forms & confirmations
│   ├── static/css/style.css      # Dark theme stylesheet
│   ├── manage.py                 # Django CLI
│   └── db.sqlite3                # SQLite database
└── venv/                         # Virtual environment (not committed)
```

---

## ⚙️ Installation Guide

### 1. Clone & Setup Environment

```bash
git clone <repo_url>
cd PEP_CAPSTONE
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Mac/Linux
```

### 2. Install Dependencies

```bash
pip install django djangorestframework
```

### 3. Database Setup

```bash
cd storemanagement
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Admin User

```bash
python manage.py createsuperuser
```

### 5. Run Server

```bash
python manage.py runserver
```

Then visit:
- 🏠 **Customer Storefront:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 🔧 **Admin Dashboard:** [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/) *(staff login required)*
- ⚙️ **Django Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- 📡 **REST API:** [http://127.0.0.1:8000/api/products/](http://127.0.0.1:8000/api/products/)

---

## 🔌 API Endpoints

### REST API (DRF)

| Method | Endpoint              | Description                   | Auth Required |
|--------|-----------------------|-------------------------------|---------------|
| GET    | `/api/products/`      | List all products             | ❌ No         |
| POST   | `/api/products/`      | Create a product              | ❌ No         |
| GET    | `/api/products/<id>/` | Product details               | ❌ No         |
| PUT    | `/api/products/<id>/` | Update a product              | ❌ No         |
| DELETE | `/api/products/<id>/` | Delete a product              | ❌ No         |

### Web Application Routes

| Method | Endpoint                      | Description                   | Auth Required  |
|--------|-------------------------------|-------------------------------|----------------|
| GET    | `/`                           | Customer storefront (home)    | ❌ No          |
| POST   | `/order/`                     | Place an order (JSON body)    | ❌ No          |
| GET    | `/login/`                     | Admin login page              | ❌ No          |
| GET    | `/logout/`                    | Logout                        | ❌ No          |
| GET    | `/dashboard/`                 | Inventory dashboard           | ✅ Staff only  |
| GET    | `/revenue/`                   | Revenue & order analytics     | ✅ Staff only  |
| GET    | `/products/add/`              | Add product form              | ✅ Staff only  |
| GET    | `/products/<id>/edit/`        | Edit product form             | ✅ Staff only  |
| POST   | `/products/<id>/delete/`      | Delete product                | ✅ Staff only  |
| POST   | `/products/<id>/stock/`       | Update stock (add/reduce)     | ✅ Staff only  |

### API Filtering Examples

```
GET /api/products/?name=Laptop
GET /api/products/?category=electronics
GET /api/products/?min_price=100&max_price=500
GET /api/products/?in_stock=true
GET /api/products/?category=electronics&min_price=100&in_stock=true
```

---

## 🧪 Testing with Postman

### Creating a Product (API)

```
POST http://127.0.0.1:8000/api/products/
Content-Type: application/json

{
  "name": "MacBook Pro",
  "description": "Apple laptop",
  "price": "1999.99",
  "stock": 25,
  "category": 1
}
```

### Placing an Order (Web)

```
POST http://127.0.0.1:8000/order/
Content-Type: application/json

{
  "items": [
    {"id": 1, "quantity": 2},
    {"id": 3, "quantity": 1}
  ]
}
```

### Common Pitfalls & Fixes

- **404 Errors:** Django URLs need a trailing slash. Use `http://.../api/products/`, not `.../api/products`.
- **CSRF Errors on Order:** Ensure your request includes the CSRF token or use the API endpoint.
- **"Page not found" on Dashboard:** You must be logged in as a **staff user** (`is_staff=True`).

---

## 🔧 Django Admin Customization

The Django Admin panel at `/admin/` is enhanced with:

- **ProductAdmin:** Displays `name`, `price`, `category`, `stock` with filtering by category.
- **OrderAdmin:** Displays order details with **inline OrderItems** (read-only tabular view).
- **OrderItemAdmin:** Shows line-item details with computed `line_total`.
- **CategoryAdmin:** Simple category management with search.

## 📞 Contact

Ready to discuss **Web Dev** or share **interview experiences**? Let's connect!

**Anugrah K.**  
*AI & Cybersecurity Enthusiast*  

📧 [Email](mailto:anugrah.k910@gmail.com)  
🔗 [GitHub](https://github.com/anugrahk21)  
💼 [LinkedIn](https://linkedin.com/in/anugrah-k)