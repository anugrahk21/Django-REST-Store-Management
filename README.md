# Django-REST-Store-Management 🛒

## 📋 Project Overview
This repository hosts the **Backend Core** of **Django-REST-Store-Management**. Built with **Django** and **Django REST Framework (DRF)**, it is a production-ready RESTful API designed to power modern store inventory systems.

While the project includes (or will include) a frontend interface, the **primary focus** here is on the backend architecture: providing a secure, scalable, and efficient **REST API** to handle inventory, authentication, and data logic.

---

## 📚 Key Learnings & Concepts Implemented
This project was built step-by-step, incorporating the following core Django & REST API concepts:

### 1. 🏗️ Project Structure & Setup
- **Project vs. App**:
  - `mainproject/`: The configuration root (settings, urls).
  - `app/`: The specific functionality (models, views for products).
- **Environment**: Used `venv` for dependency isolation.
- **Commands used**:
  ```bash
  django-admin startproject core .  # Start project in current dir
  python manage.py startapp app     # Create the app
  ```

### 2. �️ Database & Models
- **Models**: Defined `Product` with fields like `CharField`, `DecimalField`, and `ImageField`.
- **Media Handling**: strictly requires `Pillow` library for image processing.
- **Migrations**:
  - `makemigrations`: Prepares the blueprint for DB changes.
  - `migrate`: Applies changes to the actual `db.sqlite3` file.
  - **Learning**: Adding a non-nullable field to existing data requires a **default value** to fix migration errors.

### 3. 🚀 Django REST Framework (DRF)
- **Serializers**: The bridge between complex database objects and JSON.
  - Used `ModelSerializer` to automatically map `Product` model to JSON.
- **ViewSets**:
  - `ModelViewSet` provided instant **CRUD** (Create, Read, Update, Delete) without writing manual views.
- **Routers**:
  - `DefaultRouter` automatically generated URLs for the ViewSet (`/products/`).

### 4. 🔐 Authentication (JWT)
Implemented **Stateless Authentication** using `SimpleJWT`.
- **Why JWT?**: APIs don't use cookies/sessions like browsers. Validating identity requires a token on *every request*.
- **The Flow**:
  1. **Login** (`POST /login/`) → Server validates credentials.
  2. **Receive Tokens**:
     - **Access Token** 🎫: Short-lived (~5 mins). Your "Key Card" for API access.
     - **Refresh Token** 🔄: Long-lived. Used to get a new Access Token when the old one expires.
  3. **Request Data**: Send Access Token in the Header: `Authorization: Bearer <token>`.

### 5. 🔍 Custom Filtering
- Implemented `get_queryset` override to filter data dynamically.
- **Params**: `?category=electronics` or `?name=MacBook`.
- **Settings Gotcha**: In `settings.py`, a single-item tuple *must* have a trailing comma: `('item',)` not `('item')`.

---

## 🛠️ Tech Stack
- **Core**: Python 3.10+, Django 5.x
- **API**: Django REST Framework (DRF)
- **Auth**: `djangorestframework-simplejwt`
- **Utils**: `Pillow` (Images), `django-filter` (Advanced filtering)

---

## ⚙️ Installation Guide

1. **Clone & Setup Environment**
   ```bash
   git clone <repo_url>
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate # Mac/Linux
   ```

2. **Install Dependencies**
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt pillow django-filter
   ```

3. **Database Setup**
   ```bash
   cd mainproject
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Admin User**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run Server**
   ```bash
   python manage.py runserver
   ```

---

## 🧪 Testing with Postman
**Common Pitfalls & Fixes Encountered:**
1. **404 Errors on Auth**: Django URLs need a trailing slash. Use `http://.../login/`, not `.../login`.
2. **File Uploads**:
   - Method: `POST`
   - Body: `form-data`
   - Key Type: Change from **Text** to **File** for images.
   - **Do NOT** manually set `Content-Type` header (Postman handles it).
3. **Auth Error**: "Authentication credentials were not provided"
   - Fix: Add `Authorization` header with type `Bearer Token` and paste your access token.

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/login/` | Get Access/Refresh Tokens | ❌ No |
| `POST` | `/refresh/` | Refresh expired Access Token | ❌ No |
| `GET` | `/products/` | List all products | ✅ Yes |
| `POST` | `/products/` | Create product (form-data) | ✅ Yes |
| `GET`  | `/products/<id>/` | Product details | ✅ Yes |
| `PUT`  | `/products/<id>/` | Update product | ✅ Yes |
| `DEL`  | `/products/<id>/` | Delete product | ✅ Yes |

**Filtering Examples:**
- `GET /products/?category=electronics`
- `GET /products/?name=Laptop`
