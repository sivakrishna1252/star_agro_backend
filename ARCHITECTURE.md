# Star Agsurf Industries — Backend Architecture

> **Version 2** — Product Management & Inquiry Management Platform  
> Local development only — Django + DRF + PostgreSQL + Django Admin + CKEditor

---

## 1. System Architecture

```
Frontend (React/Next.js) — separate team
         │
         │  HTTP/JSON (REST)
         ▼
Django REST Framework  (/api/*)
         │
    ┌────┴────────────────┐
    ▼                     ▼
Django Admin          Django ORM
(CKEditor CMS)            │
    │                     ▼
    ▼              PostgreSQL (star_agro)
Local Media
(media/)
```

### Data Flow

| Action | Flow |
|--------|------|
| Browse products | Frontend → `GET /api/products/` → **published only** → JSON |
| Product cards | API returns `thumbnail_url` (thumbnail → gallery fallback) |
| Product detail | `GET /api/products/{slug}/` → properties, benefits, applications, documents |
| Product inquiry | `POST /api/inquiries/` → stores product_id + product_name + source |
| General contact | `POST /api/contact/` → ContactMessage (no product link) |
| Company docs | `GET /api/company-documents/` → PDFs not tied to products |
| CMS content | Admin → Site Settings (rich text) → `GET /api/site-settings/` |
| Lead management | Admin → Inquiries + Inquiry Notes timeline |

---

## 2. Complete Database Schema

```
User (Django auth)
│
Category ──< Product ──< ProductImage        (gallery)
              ├──< ProductProperty           (dynamic specs)
              ├──< ProductBenefit            (dynamic benefits)
              ├──< ProductApplication        (dynamic applications)
              ├──< ProductDocument           (product PDFs)
              ├──< ProductMetric             (future analytics)
              └──< Inquiry ──< InquiryNote    (internal timeline)

ProductDocument ──< DocumentDownloadLog      (future analytics)

CompanyDocument                              (company-level PDFs)
ContactMessage                               (general contact form)
SiteSettings                                 (singleton CMS)
```

---

## 3. Models Reference

### Product (V2 updates)

| Field | Type | Purpose |
|-------|------|---------|
| status | draft / published / archived | Only **published** in public APIs |
| thumbnail | ImageField | Listing cards, featured, search (separate from gallery) |
| display_order | PositiveIntegerField | Admin-controlled sort order |
| created_by | FK → User | Auto-set on create in admin |
| updated_by | FK → User | Auto-set on update in admin |
| description | RichTextField (CKEditor) | Formatted product content |
| is_featured | BooleanField | Homepage featured section |

**Removed:** `is_active` (replaced by `status`)

**QuerySet helper:** `Product.objects.published()`

### ProductImage (Gallery — V1)

| Field | Type |
|-------|------|
| product | FK → Product |
| image | ImageField |
| alt_text | CharField |
| display_order | PositiveIntegerField |
| is_primary | BooleanField |

### ProductProperty (V1)

| Field | Type |
|-------|------|
| property_name | CharField (e.g. Appearance, pH) |
| property_value | CharField (e.g. Pale Yellow Liquid) |
| display_order | PositiveIntegerField |

### ProductBenefit (V1)

| Field | Type |
|-------|------|
| benefit | CharField |
| display_order | PositiveIntegerField |

### ProductApplication (V1)

| Field | Type |
|-------|------|
| application_text | CharField |
| display_order | PositiveIntegerField |

### ProductDocument (V1)

| Field | Type |
|-------|------|
| document_name | CharField |
| document_type | TDS, BROCHURE, CATALOG, MSDS, PRODUCT_SHEET |
| file | FileField |
| display_order | PositiveIntegerField |

### CompanyDocument (V2)

| Field | Type |
|-------|------|
| title | CharField |
| document_type | COMPANY_PROFILE, COMPANY_BROCHURE, CERTIFICATE, TECHNICAL_CATALOG, OTHER |
| pdf_file | FileField |
| display_order | PositiveIntegerField |
| is_active | BooleanField |

### Category (V1 + SEO)

| Field | Type |
|-------|------|
| slug | SlugField |
| meta_title | CharField |
| meta_description | TextField |

### Inquiry (V1 + V2)

| Field | Type |
|-------|------|
| product | FK → Product (nullable) |
| product_name | CharField (snapshot) |
| source | website / product_page / contact_page |
| status | new / contacted / qualified / closed |

### InquiryNote (V2)

| Field | Type |
|-------|------|
| inquiry | FK → Inquiry |
| note | TextField |
| created_by | FK → User |
| created_at | DateTimeField |

Admin-only — not exposed in public APIs.

### ContactMessage (V2)

| Field | Type |
|-------|------|
| name, email, phone | Contact info |
| subject | CharField |
| message | TextField |
| status | new / read / replied / closed |
| created_at | DateTimeField |

### SiteSettings (V1 + V2 CMS)

| Field | Type |
|-------|------|
| site_name | CharField |
| company_logo | ImageField |
| about_us, vision, mission | RichTextField (CKEditor) |
| contact_email, phone, address | Contact fields |
| whatsapp_number | CharField |
| social media URLs | URLField |

### Future-Ready (V1)

| Model | Purpose |
|-------|---------|
| ProductMetric | view_count, inquiry_count, download_count |
| DocumentDownloadLog | Per-download tracking |

---

## 4. Product Status Rules

| Status | Public API | Django Admin |
|--------|-----------|--------------|
| Draft | Hidden | Visible, editable |
| Published | Visible | Visible, editable |
| Archived | Hidden | Visible, editable |

All public product endpoints filter with `Product.objects.published()`.

---

## 5. Django Admin (V2)

| Module | Capabilities |
|--------|-------------|
| **Products** | Status, thumbnail, display order, created/updated by, 5 inlines (images, properties, benefits, applications, documents), CKEditor description |
| **Categories** | CRUD, SEO fields, ordering |
| **Product Documents** | Per-product PDF management |
| **Company Documents** | Company profile, brochure, certificates, catalogs |
| **Inquiries** | Status, source, product snapshot, **Inquiry Notes** inline timeline |
| **Inquiry Notes** | Standalone admin for note management |
| **Contact Messages** | `/admin/contact/contactmessage/` — general visitor messages |
| **Site Settings** | Logo, rich text About/Vision/Mission, contact & social |

**Admin URL:** http://127.0.0.1:8000/admin/  
**Credentials (local):** admin / admin123

---

## 6. REST API — Complete Endpoint List

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | Active categories with SEO + product counts |
| GET | `/api/products/` | Published products with filters |
| GET | `/api/products/search/?q=` | Search published products |
| GET | `/api/products/{slug}/` | Full product detail |
| GET | `/api/featured-products/` | Featured published products (by display_order) |
| GET | `/api/documents/` | Product documents |
| GET | `/api/company-documents/` | Company-level documents |
| POST | `/api/inquiries/` | Product/distributor inquiry |
| POST | `/api/contact/` | General contact message |
| GET | `/api/site-settings/` | CMS content + logo URL |
| GET | `/api/search/` | Global search (products + categories) |

### Product Filtering

| Query Param | Example | Description |
|-------------|---------|-------------|
| `category` | `sc-formulations` | Category slug |
| `formulation_type` | `SC` | Formulation type |
| `formulation` | `EC` | Alias for formulation_type |
| `product_type` | `SC` | Formulation OR category slug |
| `featured` | `true` | Featured products only |

Works on `/api/products/` and `/api/products/search/`.

### Product List Card Response

```json
{
  "name": "STAGSURF SC 6875",
  "slug": "stagsurf-sc-6875",
  "display_order": 5,
  "thumbnail_url": "http://127.0.0.1:8000/media/products/thumbnails/....jpg",
  "is_featured": false
}
```

`thumbnail_url` priority: **thumbnail field → primary gallery image → first gallery image**

### Product Detail — Dynamic Fields

```json
{
  "description": "<p>Rich HTML from CKEditor</p>",
  "properties": [{"property_name": "Appearance", "property_value": "Pale Yellow Liquid"}],
  "benefits": [{"benefit": "Increases herbicide penetration"}],
  "applications": [{"application_text": "Crop Protection"}],
  "documents": [{"document_name": "TDS", "document_type": "TDS", "file_url": "..."}]
}
```

### POST `/api/inquiries/`

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+919876543210",
  "company": "Agri Distributors Ltd",
  "product_slug": "stagsurf-sc-6875",
  "source": "product_page",
  "message": "Interested in bulk supply."
}
```

**Response (201):**
```json
{
  "success": true,
  "inquiry_id": 1,
  "product_id": 6,
  "product_name": "STAGSURF SC 6875"
}
```

**Source values:** `website`, `product_page`, `contact_page`  
Auto-defaults to `product_page` when a product is linked.

### POST `/api/contact/`

**Request:**
```json
{
  "name": "Jane Smith",
  "email": "jane@company.com",
  "phone": "+919876543210",
  "subject": "Partnership Inquiry",
  "message": "We would like to discuss distribution partnership."
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Your message has been sent successfully.",
  "contact_id": 1
}
```

---

## 7. Media Upload System

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

```
media/
├── categories/
├── products/
│   ├── thumbnails/     # Product listing cards (V2)
│   └── images/         # Product gallery (V1)
├── documents/
│   ├── products/       # Product PDFs
│   └── company/        # Company documents (V2)
└── site/               # Company logo
```

---

## 8. Rich Text Editor (V2)

**Package:** `django-ckeditor`

**Rich text fields:**
- `Product.description`
- `SiteSettings.about_us`
- `SiteSettings.vision`
- `SiteSettings.mission`

Admin supports: headings, bold, lists, tables, links, formatted content.

---

## 9. Folder Structure

```
Star agro/
├── manage.py
├── requirements.txt
├── .env
├── ARCHITECTURE.md          ← this file
├── README.md
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── admin.py
├── apps/
│   ├── categories/
│   ├── products/            # Product + gallery + properties + benefits + applications
│   ├── documents/           # ProductDocument + CompanyDocument
│   ├── inquiries/           # Inquiry + InquiryNote
│   ├── contact/             # ContactMessage (V2)
│   └── site_settings/       # SiteSettings CMS
├── api/
│   ├── serializers/
│   └── views/
├── media/
└── static/
```

---

## 10. Categories (Seed Data)

1. Crop Protection  
2. SC Formulations  
3. EC Formulations  
4. ME Formulations  
5. EW Formulations  
6. Adjuvants  
7. Wetting Agents  
8. Dispersing Agents  
9. Textile Chemicals  

---

## 11. Future-Ready Design

| Future Feature | Schema Support |
|----------------|----------------|
| Dealer Portal | Extend Django User + DealerProfile |
| Distributor Login | User roles + permissions |
| Product Comparison | Compare product IDs via relational API |
| Download Analytics | DocumentDownloadLog model ready |
| Product View Analytics | ProductMetric.view_count ready |
| Lead Source Analytics | Inquiry.source field (V2) |

---

## 12. Development Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: Database Design | ✅ Done | V1 + V2 schema |
| Phase 2: Models | ✅ Done | All models + migrations |
| Phase 3: Admin Panel | ✅ Done | Full admin + CKEditor |
| Phase 4: REST APIs | ✅ Done | All public endpoints |
| Phase 5: Testing | Pending | Unit + integration tests |
| Phase 6: Frontend Integration | Ready | CORS enabled for localhost:3000 |

---

## 13. Quick Start

```powershell
cd "C:\Users\VivekNookala\Desktop\Star agro"
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

| Service | URL |
|---------|-----|
| Django Admin | http://127.0.0.1:8000/admin/ |
| REST API | http://127.0.0.1:8000/api/ |
| Swagger UI | http://127.0.0.1:8000/api/docs/ |
| Frontend API Guide | [API.md](API.md) |

**Database:** PostgreSQL `star_agro` @ `127.0.0.1:5432` (see `.env`)

---

## Version History

| Version | Changes |
|---------|---------|
| **V1** | Product gallery, dynamic properties/benefits/applications, product documents, categories, inquiries, site settings CMS, search & filters, SEO fields |
| **V2** | Product status (draft/published/archived), thumbnail, created_by/updated_by, inquiry source + notes, contact messages, company documents, CKEditor rich text, published-only APIs |
