# Little Lemon API

A Django REST Framework API for the Little Lemon restaurant, providing menu management, cart functionality, order processing, and role-based access control.

## Features

- **Menu Management** - CRUD operations for menu items with categories, pricing, and featured items
- **Cart System** - Authenticated users can add/remove items and checkout
- **Order Processing** - Role-based order access (Manager sees all, Delivery Crew sees assigned, Customers see own)
- **User Groups** - Manager and Delivery Crew groups with dedicated management endpoints
- **Authentication** - Token-based auth via Djoser (register, login, logout)
- **Permissions** - Custom role-based permissions (Manager, Delivery Crew, Customer)
- **Throttling** - Rate limiting (5 requests/minute for both authenticated and anonymous users)
- **Pagination** - PageNumberPagination with 3 items per page

## Tech Stack

- **Framework**: Django 5.x + Django REST Framework
- **Auth**: Djoser (token + session authentication)
- **Database**: SQLite (development)
- **Python**: 3.14+

## Project Structure

```
LittleLemonAPI/
├── LittleLemon/           # Django project config
│   ├── settings.py        # Project settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI entrypoint
│   └── asgi.py            # ASGI entrypoint
├── LittleLemonAPI/        # Main application
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── permissions.py     # Custom permissions
│   ├── urls.py            # App URL routing
│   ├── admin.py           # Admin configuration
│   ├── apps.py            # App config
│   ├── tests.py           # Test cases (placeholder)
│   └── migrations/        # Database migrations
├── manage.py              # Django management script
├── Pipfile                # Python dependencies
├── Pipfile.lock           # Locked dependencies
└── db.sqlite3             # SQLite database (created after migrate)
```

## API Endpoints

### Authentication (`/auth/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/users/` | Register new user |
| POST | `/auth/token/login/` | Login (get token) |
| POST | `/auth/token/logout/` | Logout (invalidate token) |

### Menu Items (`/api/`)
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/menu-items` | Public | List menu items (filtering, search, ordering) |
| POST | `/api/menu-items` | Manager | Create menu item |
| GET | `/api/menu-items/{id}` | Public | Get single menu item |
| PUT/PATCH | `/api/menu-items/{id}` | Manager | Update menu item |
| DELETE | `/api/menu-items/{id}` | Manager | Delete menu item |

### Cart (`/api/cart/`)
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/cart/menu-items` | Authenticated | View cart |
| POST | `/api/cart/menu-items` | Authenticated | Add item to cart |
| DELETE | `/api/cart/menu-items` | Authenticated | Clear cart |

### Orders (`/api/orders/`)
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/orders` | Role-based | List orders (Manager=all, Crew=assigned, Customer=own) |
| POST | `/api/orders` | Authenticated | Create order from cart |
| GET | `/api/orders/{id}` | Role-based | Get order detail |
| PATCH | `/api/orders/{id}` | Manager/Crew | Update order (Manager=full, Crew=status only) |
| DELETE | `/api/orders/{id}` | Manager | Delete order |

### User Groups (`/api/groups/`)
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/groups/manager/users` | Manager | List Manager group users |
| POST | `/api/groups/manager/users` | Manager | Add user to Manager group |
| DELETE | `/api/groups/manager/users/{id}` | Manager | Remove user from Manager group |
| GET | `/api/groups/delivery-crew/users` | Manager | List Delivery Crew users |
| POST | `/api/groups/delivery-crew/users` | Manager | Add user to Delivery Crew group |
| DELETE | `/api/groups/delivery-crew/users/{id}` | Manager | Remove user from Delivery Crew group |

## Getting Started

### Prerequisites

- Python 3.14+
- pipenv (or pip + venv)

### Installation

```bash
# Clone the repository
cd LittleLemonAPI

# Install dependencies using pipenv
pipenv install

# Or with pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt  # Generate from Pipfile if needed
```

### Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

### Default Admin

- Admin panel: `http://localhost:8000/admin/`

## User Roles & Permissions

| Role | Menu Items | Cart | Orders | User Groups |
|------|------------|------|--------|-------------|
| **Manager** | Full CRUD | View own | All (CRUD) | Manage Manager & Delivery Crew |
| **Delivery Crew** | Read only | View own | Assigned (read + status update) | None |
| **Customer** | Read only | Full (own) | Own (read + create) | None |

## Testing

```bash
# Run tests
python manage.py test
```

> Note: Tests are currently a placeholder in `LittleLemonAPI/tests.py`

## Environment Variables

Key settings in `LittleLemon/settings.py`:
- `SECRET_KEY` - Django secret key (change in production!)
- `DEBUG` - Set to `False` in production
- `ALLOWED_HOSTS` - Add your domain(s) in production
- `DATABASES` - SQLite by default; configure PostgreSQL/MySQL for production

## Production Deployment

1. Set `DEBUG = False`
2. Set `SECRET_KEY` from environment variable
3. Configure `ALLOWED_HOSTS`
4. Use PostgreSQL or MySQL instead of SQLite
5. Set up static file serving (`collectstatic`)
6. Use a production WSGI/ASGI server (Gunicorn, uWSGI)
7. Configure HTTPS and security headers

## License

This project is for educational/demo purposes.