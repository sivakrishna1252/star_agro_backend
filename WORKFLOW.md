# Star Agsurf Industries — Complete System Workflow

> One document explaining how the entire backend works — for admins, developers, and the frontend team.  
> Version 2 | Local development | Django + PostgreSQL + Django Admin + REST API

---

## Table of Contents

1. [Big Picture — Who Does What](#1-big-picture--who-does-what)
2. [System Layers](#2-system-layers)
3. [Admin Workflow — Daily Operations](#3-admin-workflow--daily-operations)
4. [Product Lifecycle Workflow](#4-product-lifecycle-workflow)
5. [Website Visitor Workflows (Frontend + API)](#5-website-visitor-workflows-frontend--api)
6. [Lead & Contact Workflows](#6-lead--contact-workflows)
7. [Content Management Workflow (CMS)](#7-content-management-workflow-cms)
8. [Document Management Workflow](#8-document-management-workflow)
9. [Search & Filter Workflow](#9-search--filter-workflow)
10. [Media & File Storage Workflow](#10-media--file-storage-workflow)
11. [End-to-End Scenario Examples](#11-end-to-end-scenario-examples)
12. [Quick Reference](#12-quick-reference)

---

## 1. Big Picture — Who Does What

```
┌─────────────────────────────────────────────────────────────────────┐
│                        THREE ACTORS                                  │
├─────────────────┬───────────────────────┬───────────────────────────┤
│  ADMIN STAFF    │  WEBSITE VISITOR      │  FRONTEND (React/Next.js) │
│  (Django Admin) │  (Browser)            │  (Separate team)          │
├─────────────────┼───────────────────────┼───────────────────────────┤
│ Creates products│ Browses products      │ Calls REST APIs           │
│ Uploads PDFs    │ Downloads documents   │ Renders JSON as UI        │
│ Manages leads   │ Submits inquiries     │ Posts forms to backend    │
│ Updates About Us│ Sends contact msgs    │ Never talks to DB direct  │
└─────────────────┴───────────────────────┴───────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   STAR AGRO DJANGO BACKEND     │
              │   Admin Panel  +  REST API     │
              │   PostgreSQL   +  Media Files  │
              └───────────────────────────────┘
```

| Actor | Tool | Purpose |
|-------|------|---------|
| **Admin** | http://127.0.0.1:8000/admin/ | Manage all data — products, leads, content, documents |
| **Visitor** | Public website (built by frontend team) | View products, submit forms |
| **Frontend** | React/Next.js app | Fetches data from `/api/*`, displays to visitor |

**Admin login (local dev):** username `admin` | password `admin123`

---

## 2. System Layers

Every request follows this path:

```
Visitor / Frontend
        │
        ▼  HTTP request (GET or POST)
┌───────────────────┐
│  Django REST API  │  ← Public read + form submissions
│  /api/*           │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Serializers      │  ← Validate input, format JSON output
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Django ORM       │  ← Query / save models
└─────────┬─────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
PostgreSQL    Media folder
(star_agro)   (images, PDFs)
```

**Admin path (separate from API):**

```
Admin browser → /admin/ → Django Admin → ORM → PostgreSQL + Media
```

Admin never needs the REST API. Frontend never needs Django Admin.

---

## 3. Admin Workflow — Daily Operations

### 3.1 Login & Dashboard

```
1. Open http://127.0.0.1:8000/admin/
2. Login with admin credentials
3. Dashboard shows all modules:
   ├── Categories
   ├── Products
   ├── Product Images / Properties / Benefits / Applications
   ├── Product Documents
   ├── Company Documents
   ├── Inquiries (+ Inquiry Notes)
   ├── Contact Messages
   └── Site Settings
```

### 3.2 Typical Admin Day

```
Morning                          During day                    End of day
────────                         ──────────                    ──────────
Check new Inquiries      →    Update product content    →   Mark leads as
Check Contact Messages         Upload new PDFs                 Contacted / Closed
Review draft products          Publish ready products          Add Inquiry Notes
Update Site Settings           Reorder featured products
```

---

## 4. Product Lifecycle Workflow

This is the core workflow for managing products.

### 4.1 Creating a New Product

```
STEP 1 — Create Category (if needed)
   Admin → Categories → Add
   Fields: name, slug, description, image, SEO fields

STEP 2 — Create Product (as Draft)
   Admin → Products → Add
   ├── Basic: name, slug, category, formulation type
   ├── Status: DRAFT (default — not visible on website yet)
   ├── Thumbnail: upload listing card image
   ├── Display order: set sort position (0 = first)
   └── Description: write with CKEditor (rich text)

STEP 3 — Add Related Data (inlines on same page)
   ├── Product Images      → gallery photos (multiple)
   ├── Product Properties  → Appearance: Pale Yellow Liquid, pH: 5-7, etc.
   ├── Product Benefits    → Increases penetration, Improves retention, etc.
   ├── Product Applications→ Crop Protection, Textile Industry, etc.
   └── Product Documents   → upload TDS, Brochure, MSDS PDFs

STEP 4 — Save
   System records: created_by = current admin user

STEP 5 — Publish
   Change status: DRAFT → PUBLISHED
   Product now appears on frontend via API
```

### 4.2 Product Status Rules

```
                    ┌─────────┐
         create ──► │  DRAFT  │ ── not visible on website
                    └────┬────┘
                         │ admin sets PUBLISHED
                         ▼
                    ┌───────────┐
                    │ PUBLISHED │ ── visible on website ✓
                    └─────┬─────┘
                          │ admin sets ARCHIVED
                          ▼
                    ┌───────────┐
                    │ ARCHIVED  │ ── hidden from website (old/discontinued)
                    └───────────┘
```

| Status | Public API | Use case |
|--------|-----------|----------|
| Draft | Hidden | Work in progress |
| Published | Visible | Live on website |
| Archived | Hidden | Discontinued product, keep records |

### 4.3 Featured Products

```
Admin marks product: is_featured = ✓
         │
         ▼
Frontend calls: GET /api/featured-products/
         │
         ▼
Returns published + featured products, sorted by display_order
         │
         ▼
Homepage shows featured product cards with thumbnail_url
```

### 4.4 Thumbnail vs Gallery

```
Product
├── thumbnail          → used for: listing cards, search results, featured section
└── images (gallery)   → used for: product detail page photo gallery

API priority for card image (thumbnail_url):
   1. thumbnail field (if uploaded)
   2. primary gallery image (is_primary = true)
   3. first gallery image
   4. null (no image)
```

---

## 5. Website Visitor Workflows (Frontend + API)

These are the journeys a visitor takes. The frontend team implements the UI; the backend provides the data.

### 5.1 Homepage Load

```
Visitor opens homepage
        │
        ▼
Frontend makes parallel API calls:
        │
        ├── GET /api/site-settings/        → company name, logo, about snippet
        ├── GET /api/featured-products/    → 4 featured product cards
        └── GET /api/categories/           → category navigation menu
        │
        ▼
Frontend renders homepage with live data from PostgreSQL
```

### 5.2 Browse Products by Category

```
Visitor clicks "SC Formulations"
        │
        ▼
Frontend: GET /api/products/?category=sc-formulations
        │
        ▼
Backend filters: status=published AND category slug=sc-formulations
        │
        ▼
Returns product list with thumbnail_url, sorted by display_order
        │
        ▼
Frontend renders product grid
```

### 5.3 View Product Detail

```
Visitor clicks "STAGSURF SC 6875"
        │
        ▼
Frontend: GET /api/products/stagsurf-sc-6875/
        │
        ▼
Backend returns full product JSON:
   ├── description (HTML from CKEditor)
   ├── properties[]     → dynamic spec table
   ├── benefits[]       → bullet list
   ├── applications[]   → use cases
   ├── images[]         → photo gallery
   └── documents[]      → downloadable PDFs with file_url
        │
        ▼
Frontend renders product detail page
```

### 5.4 Download a Document

```
Visitor clicks "Download TDS"
        │
        ▼
Frontend uses file_url from API response
   e.g. http://127.0.0.1:8000/media/documents/products/stagsurf-tds.pdf
        │
        ▼
Browser downloads PDF directly from media folder
```

---

## 6. Lead & Contact Workflows

There are **two separate form flows** — do not confuse them.

### 6.1 Product Inquiry (B2B Lead)

**When:** Visitor is interested in a specific product or wants distributor pricing.

```
Visitor fills inquiry form on product page
        │
        ▼
Frontend: POST /api/inquiries/
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+919876543210",
  "company": "Agri Distributors Ltd",
  "product_slug": "stagsurf-sc-6875",
  "source": "product_page",
  "message": "Interested in bulk supply for EC formulations."
}
        │
        ▼
Backend validates → saves Inquiry record:
   ├── product_id = 6
   ├── product_name = "STAGSURF SC 6875"  (snapshot — kept even if product renamed)
   ├── source = product_page
   └── status = NEW
        │
        ▼
Returns: { success: true, inquiry_id: 1, product_id: 6, product_name: "..." }
        │
        ▼
Admin sees new lead in: Admin → Inquiries
```

### 6.2 General Contact Message

**When:** Visitor has a general question — not about a specific product.

```
Visitor fills contact form on Contact page
        │
        ▼
Frontend: POST /api/contact/
{
  "name": "Jane Smith",
  "email": "jane@company.com",
  "phone": "+919876543210",
  "subject": "Partnership Inquiry",
  "message": "We would like to discuss distribution partnership."
}
        │
        ▼
Backend saves ContactMessage:
   └── status = NEW
        │
        ▼
Admin sees it in: Admin → Contact Messages
```

### 6.3 Inquiry vs Contact — Decision Guide

| Situation | Use | API |
|-----------|-----|-----|
| Product-specific question | Inquiry | POST /api/inquiries/ |
| General company question | Contact | POST /api/contact/ |
| Distributor/dealer interest with product | Inquiry + product_slug | POST /api/inquiries/ |
| Partnership without specific product | Contact | POST /api/contact/ |

### 6.4 Lead Management Workflow (Admin)

```
New inquiry arrives (status: NEW)
        │
        ▼
Admin opens Inquiry in Django Admin
        │
        ├── Reviews contact details + message
        ├── Adds Inquiry Note: "Called customer — interested in bulk order"
        ├── Adds Inquiry Note: "Follow-up required next week"
        └── Updates status: NEW → CONTACTED → QUALIFIED → CLOSED
        │
        ▼
Inquiry Notes form internal timeline (never shown to visitor)
```

**Inquiry status flow:**

```
NEW ──► CONTACTED ──► QUALIFIED ──► CLOSED
 │          │              │
 └──────────┴──────────────┴── can jump to CLOSED at any stage
```

**Inquiry source tracking (for future analytics):**

| Source | Meaning |
|--------|---------|
| website | General site inquiry |
| product_page | Submitted from a product detail page |
| contact_page | Submitted from contact page |

---

## 7. Content Management Workflow (CMS)

All website text and branding is managed in one place — no hardcoded content in code.

```
Admin → Site Settings (single record)
        │
        ├── Branding: site_name, company_logo, tagline
        ├── About Us: about_us (rich text)
        ├── Vision: vision (rich text)
        ├── Mission: mission (rich text)
        ├── Contact: email, phone, address, WhatsApp
        └── Social: Facebook, LinkedIn, Instagram, Twitter, YouTube
        │
        ▼
Frontend: GET /api/site-settings/
        │
        ▼
Returns all content + company_logo_url
        │
        ▼
Frontend renders About page, footer, contact section
```

**Rule:** Frontend team must always fetch from `/api/site-settings/` — never hardcode company info.

---

## 8. Document Management Workflow

Two types of documents exist:

### 8.1 Product Documents (linked to a product)

```
Admin → Products → [select product] → Product Documents inline
   OR Admin → Product Documents

Upload: TDS, Brochure, Catalog, MSDS, Product Sheet
        │
        ▼
Stored in: media/documents/products/
        │
        ▼
Available via:
   ├── GET /api/products/{slug}/  → documents[] in product detail
   └── GET /api/documents/?product=stagsurf-sc-6875
```

### 8.2 Company Documents (not linked to any product)

```
Admin → Company Documents → Add

Upload: Company Profile, Brochure, Certificate, Technical Catalog
        │
        ▼
Stored in: media/documents/company/
        │
        ▼
Available via: GET /api/company-documents/
        │
        ▼
Frontend shows on Downloads / Resources page
```

---

## 9. Search & Filter Workflow

### 9.1 Product Search

```
Visitor types "stagsurf" in search box
        │
        ▼
Frontend: GET /api/products/search/?q=stagsurf
        │
        ▼
Backend searches published products by:
   ├── product name
   ├── product code
   ├── category name
   └── formulation type
        │
        ▼
Returns matching products with thumbnail_url
```

### 9.2 Global Search (products + categories)

```
Frontend: GET /api/search/?q=surfactant
        │
        ▼
Returns mixed results:
   ├── type: "product"  → product cards
   └── type: "category" → category links
```

### 9.3 Filtering Products

```
All filters work on GET /api/products/ and GET /api/products/search/

?category=sc-formulations     → only SC Formulation category
?formulation_type=SC          → only SC formulation type
?featured=true                → only featured products
?product_type=adjuvants       → category slug OR formulation match

Filters can be combined:
GET /api/products/?category=sc-formulations&formulation_type=SC&featured=true
```

---

## 10. Media & File Storage Workflow

```
Admin uploads file in Django Admin
        │
        ▼
Django saves to MEDIA_ROOT on disk:

media/
├── categories/              ← category banner images
├── products/
│   ├── thumbnails/          ← product listing card images
│   └── images/              ← product gallery photos
├── documents/
│   ├── products/            ← product TDS, brochures, MSDS
│   └── company/             ← company profile, certificates
└── site/                    ← company logo

        │
        ▼
API returns absolute URLs:
   http://127.0.0.1:8000/media/products/thumbnails/image.jpg

        │
        ▼
Frontend uses URL directly in <img src=""> or <a href=""> for downloads
```

---

## 11. End-to-End Scenario Examples

### Scenario A — Admin publishes a new product

```
1. Admin creates product "STAGWET NEW 100" as DRAFT
2. Adds properties: Appearance, pH, Solid Content
3. Adds benefits and applications
4. Uploads thumbnail + 3 gallery images
5. Uploads TDS PDF
6. Sets display_order = 3
7. Changes status to PUBLISHED
8. Frontend immediately shows product in GET /api/products/
9. If is_featured=true, also appears in GET /api/featured-products/
```

### Scenario B — Distributor submits product inquiry

```
1. Distributor visits product page on website
2. Fills inquiry form with company name and message
3. Frontend POST /api/inquiries/ with product_slug
4. Backend saves inquiry with status=NEW, source=product_page
5. Admin logs in, sees new inquiry
6. Admin adds note: "Called — wants 500L trial order"
7. Admin updates status to CONTACTED
8. Later updates to QUALIFIED → CLOSED
```

### Scenario C — Visitor downloads company brochure

```
1. Frontend loads GET /api/company-documents/
2. Shows list: Company Profile, Brochure, Certificate
3. Visitor clicks Brochure download link (file_url)
4. PDF opens/downloads from media/documents/company/
```

### Scenario D — Frontend builds homepage

```
Parallel API calls on page load:

GET /api/site-settings/       → logo, tagline, contact info
GET /api/featured-products/   → 4 product cards with thumbnails
GET /api/categories/            → navigation menu

All data is live from admin — no code changes needed when content updates.
```

---

## 12. Quick Reference

### API Endpoints

| Method | URL | Who uses it | Purpose |
|--------|-----|-------------|---------|
| GET | /api/categories/ | Frontend | Category list |
| GET | /api/products/ | Frontend | Product listing |
| GET | /api/products/{slug}/ | Frontend | Product detail |
| GET | /api/featured-products/ | Frontend | Homepage featured |
| GET | /api/products/search/?q= | Frontend | Product search |
| GET | /api/documents/ | Frontend | Product PDFs |
| GET | /api/company-documents/ | Frontend | Company PDFs |
| GET | /api/site-settings/ | Frontend | CMS content |
| GET | /api/search/ | Frontend | Global search |
| POST | /api/inquiries/ | Frontend | Product inquiry form |
| POST | /api/contact/ | Frontend | Contact form |

### Admin Modules

| Module | URL path | Purpose |
|--------|----------|---------|
| Products | /admin/products/product/ | Full product management |
| Categories | /admin/categories/category/ | Product categories |
| Inquiries | /admin/inquiries/inquiry/ | B2B leads |
| Contact Messages | /admin/contact/contactmessage/ | General messages |
| Company Documents | /admin/documents/companydocument/ | Company PDFs |
| Site Settings | /admin/site_settings/sitesettings/ | Website content |

### Key Rules

| Rule | Detail |
|------|--------|
| Only PUBLISHED products appear in API | Draft and Archived are admin-only |
| thumbnail_url on cards | thumbnail → primary image → first image |
| product_name on inquiry | Snapshot — preserved even if product is renamed |
| Inquiry Notes | Admin only — never in public API |
| Site Settings | Single record — one source of truth for all company info |
| display_order | Lower number = appears first in lists |

### Local Development

```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

| Service | URL |
|---------|-----|
| Django Admin | http://127.0.0.1:8000/admin/ |
| REST API | http://127.0.0.1:8000/api/ |
| API browser test | http://127.0.0.1:8000/api/products/ |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical schema, models, API specs |
| [README.md](README.md) | Setup and quick start |

---

*Star Agsurf Industries Backend — Workflow Document v2.0*
