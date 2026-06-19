# Star Agsurf Industries — Django Backend (V2)

Local development backend for Product Management & Inquiry Management.

## Stack

- Django 5.2 + Django REST Framework
- PostgreSQL (`star_agro`)
- Django Admin + CKEditor

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | Categories |
| GET | `/api/products/` | Published products (filterable) |
| GET | `/api/products/search/?q=` | Search products |
| GET | `/api/products/{slug}/` | Product detail |
| GET | `/api/featured-products/` | Featured products |
| GET | `/api/documents/` | Product documents |
| GET | `/api/company-documents/` | Company documents |
| POST | `/api/inquiries/` | Product inquiry |
| GET | `/api/contact/reasons/` | Contact form reason options |
| POST | `/api/contact/` | General contact message |
| GET | `/api/site-settings/` | CMS content |
| GET | `/api/search/` | Global search |

### Filters (`/api/products/` and `/api/products/search/`)

`category`, `formulation_type`, `formulation`, `product_type`, `featured=true`

## Admin

http://127.0.0.1:8000/admin/ — `admin` / `admin123`

Manage: product status, thumbnails, ordering, inquiry notes, contact messages, company documents.

Full documentation: **[FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)** (complete frontend guide — share with frontend team) | [API.md](API.md) | [WORKFLOW.md](WORKFLOW.md) | [ARCHITECTURE.md](ARCHITECTURE.md)

**Swagger UI:** http://127.0.0.1:8000/api/docs/
