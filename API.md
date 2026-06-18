# Star Agsurf Industries — Frontend API Integration Guide

> **Share this file with the frontend team.**  
> Version 2.0 | Base URL: `http://127.0.0.1:8000/api/` (local development)

---

## Quick Links

| Resource | URL |
|----------|-----|
| **Swagger UI (interactive)** | http://127.0.0.1:8000/api/docs/ |
| **ReDoc (readable docs)** | http://127.0.0.1:8000/api/redoc/ |
| **OpenAPI JSON schema** | http://127.0.0.1:8000/api/schema/ |
| **Workflow guide** | [WORKFLOW.md](WORKFLOW.md) |
| **Technical architecture** | [ARCHITECTURE.md](ARCHITECTURE.md) |

---

## 1. How Integration Works

```
Admin (Django Admin)  →  creates/edits content  →  PostgreSQL
                                                        ↓
Frontend (React/Next.js)  →  GET /api/*  →  reads same data  →  displays on website
Frontend forms  →  POST /api/inquiries/ or /api/contact/  →  saves leads
```

- **No authentication** required for public APIs (read + form submit).
- **Only published products** are returned (`status = published`).
- **All content** (products, About Us, contact info) comes from API — do not hardcode.
- **Admin changes** appear on the next API call automatically.

---

## 2. Base Configuration

### Base URL (local)

```
http://127.0.0.1:8000/api/
```

### Recommended `.env` for Next.js

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api
```

### Headers

```http
Content-Type: application/json
Accept: application/json
```

No `Authorization` header needed for public endpoints.

### CORS

Backend allows these origins in local dev:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

If your frontend runs on a different port, ask the backend team to add it.

### Pagination

List endpoints return paginated JSON:

```json
{
  "count": 18,
  "next": "http://127.0.0.1:8000/api/products/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

- **Page size:** 20 items per page
- **Next page:** use the `next` URL as-is, or append `?page=2`

---

## 3. Endpoint Summary

| # | Method | Endpoint | Purpose |
|---|--------|----------|---------|
| 1 | GET | `/categories/` | Category list for navigation |
| 2 | GET | `/products/` | Product listing (filterable) |
| 3 | GET | `/products/{slug}/` | Single product detail |
| 4 | GET | `/featured-products/` | Homepage featured products |
| 5 | GET | `/products/search/?q=` | Search products |
| 6 | GET | `/documents/` | Product PDF documents |
| 7 | GET | `/company-documents/` | Company-level PDFs |
| 8 | GET | `/site-settings/` | CMS: About, contact, logo |
| 9 | GET | `/search/?q=` | Global search (products + categories) |
| 10 | POST | `/inquiries/` | Product / B2B inquiry form |
| 11 | POST | `/contact/` | General contact form |

---

## 4. API Details

---

### 4.1 GET `/categories/`

List all active product categories.

**Query params:** None

**Response `200`:**

```json
{
  "count": 9,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "SC Formulations",
      "slug": "sc-formulations",
      "description": "Suspension concentrate formulation surfactants.",
      "image": null,
      "display_order": 1,
      "meta_title": "",
      "meta_description": "",
      "product_count": 7
    }
  ]
}
```

**Frontend usage:** Navigation menu, category pages, filters.

---

### 4.2 GET `/products/`

List published products. Supports filtering.

**Query params:**

| Param | Example | Description |
|-------|---------|-------------|
| `category` | `sc-formulations` | Filter by category slug |
| `formulation_type` | `SC` | Filter by formulation |
| `formulation` | `EC` | Alias for `formulation_type` |
| `product_type` | `adjuvants` | Matches formulation OR category slug |
| `featured` | `true` | Featured products only |
| `page` | `2` | Pagination |

**Example:**

```
GET /api/products/?category=sc-formulations&formulation_type=SC
```

**Response `200`:**

```json
{
  "count": 7,
  "results": [
    {
      "id": 6,
      "name": "STAGSURF SC 6875",
      "slug": "stagsurf-sc-6875",
      "product_code": "STAGSURF SC 6875",
      "short_description": "STAGSURF SC 6875 — specialty surfactant...",
      "category_name": "SC Formulations",
      "category_slug": "sc-formulations",
      "formulation_type": "SC",
      "is_featured": false,
      "display_order": 5,
      "meta_title": "",
      "meta_description": "",
      "thumbnail_url": "http://127.0.0.1:8000/media/products/thumbnails/image.jpg"
    }
  ]
}
```

**`thumbnail_url` priority:**
1. Product thumbnail (if uploaded)
2. Primary gallery image
3. First gallery image
4. `null` if no image

**Frontend usage:** Product listing grid, category product pages.

---

### 4.3 GET `/products/{slug}/`

Full product detail page data.

**Path param:** `slug` — e.g. `stagsurf-sc-6875`

**Example:**

```
GET /api/products/stagsurf-sc-6875/
```

**Response `200`:**

```json
{
  "id": 6,
  "name": "STAGSURF SC 6875",
  "slug": "stagsurf-sc-6875",
  "product_code": "STAGSURF SC 6875",
  "short_description": "...",
  "description": "<p>Rich HTML content from admin (CKEditor)</p>",
  "technical_specifications": "...",
  "formulation_type": "SC",
  "is_featured": false,
  "display_order": 5,
  "thumbnail_url": "http://127.0.0.1:8000/media/products/thumbnails/....jpg",
  "category": {
    "id": 2,
    "name": "SC Formulations",
    "slug": "sc-formulations",
    "meta_title": "",
    "meta_description": ""
  },
  "images": [
    {
      "id": 1,
      "image": "/media/products/images/photo1.jpg",
      "image_url": "http://127.0.0.1:8000/media/products/images/photo1.jpg",
      "alt_text": "Product photo",
      "is_primary": true,
      "display_order": 0
    }
  ],
  "properties": [
    {
      "id": 1,
      "property_name": "Appearance",
      "property_value": "Pale Yellow Liquid",
      "display_order": 0
    },
    {
      "id": 2,
      "property_name": "pH",
      "property_value": "5-7",
      "display_order": 1
    }
  ],
  "benefits": [
    {
      "id": 1,
      "benefit": "Increases herbicide penetration",
      "display_order": 0
    }
  ],
  "applications": [
    {
      "id": 1,
      "application_text": "Crop Protection",
      "display_order": 0
    }
  ],
  "documents": [
    {
      "id": 1,
      "document_name": "STAGSURF SC 6875 TDS",
      "document_type": "TDS",
      "file_url": "http://127.0.0.1:8000/media/documents/products/tds.pdf",
      "display_order": 0
    }
  ],
  "meta_title": "",
  "meta_description": "",
  "created_at": "2026-06-15T16:07:51+05:30",
  "updated_at": "2026-06-15T16:13:45+05:30"
}
```

**Response `404`:** Product not found or not published.

**Frontend usage:**
- Render `description` as HTML (`dangerouslySetInnerHTML` in React)
- Build specs table from `properties[]`
- Bullet list from `benefits[]`
- Application tags from `applications[]`
- Download buttons from `documents[].file_url`
- Image gallery from `images[]`
- SEO from `meta_title`, `meta_description`

---

### 4.4 GET `/featured-products/`

Published products where `is_featured = true`, sorted by `display_order`.

**Response:** Same format as `/products/` list (paginated).

**Frontend usage:** Homepage featured products section.

---

### 4.5 GET `/products/search/?q={query}`

Search published products by name, code, category, formulation.

**Query params:**

| Param | Required | Description |
|-------|----------|-------------|
| `q` | Yes | Min 2 characters |
| `category`, `formulation_type`, `featured`, etc. | No | Same filters as `/products/` |

**Example:**

```
GET /api/products/search/?q=stagsurf
```

**Response `200`:**

```json
{
  "query": "stagsurf",
  "count": 12,
  "results": [ /* same product card objects as /products/ */ ]
}
```

**Response `400`:**

```json
{
  "detail": "Search query must be at least 2 characters."
}
```

---

### 4.6 GET `/documents/`

List active product documents (PDFs).

**Query params:**

| Param | Example | Description |
|-------|---------|-------------|
| `type` | `TDS` | Document type filter |
| `product` | `stagsurf-sc-6875` | Filter by product slug |

**Document types:** `TDS`, `BROCHURE`, `CATALOG`, `MSDS`, `PRODUCT_SHEET`

**Response `200`:**

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "document_name": "STAGSURF SC 6875 TDS",
      "document_type": "TDS",
      "file_url": "http://127.0.0.1:8000/media/documents/products/tds.pdf",
      "product_name": "STAGSURF SC 6875",
      "product_slug": "stagsurf-sc-6875",
      "display_order": 0,
      "created_at": "2026-06-15T16:07:51+05:30"
    }
  ]
}
```

**Frontend usage:** Downloads page, or use documents from product detail instead.

---

### 4.7 GET `/company-documents/`

Company-level documents (not tied to a product).

**Query params:**

| Param | Example |
|-------|---------|
| `type` | `COMPANY_PROFILE` |

**Document types:** `COMPANY_PROFILE`, `COMPANY_BROCHURE`, `CERTIFICATE`, `TECHNICAL_CATALOG`, `OTHER`

**Response `200`:**

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "title": "Company Profile 2026",
      "document_type": "COMPANY_PROFILE",
      "file_url": "http://127.0.0.1:8000/media/documents/company/profile.pdf",
      "display_order": 0,
      "created_at": "2026-06-15T16:07:51+05:30"
    }
  ]
}
```

---

### 4.8 GET `/site-settings/`

All website CMS content — company info, About Us, contact, social links.

**Response `200`:**

```json
{
  "site_name": "Star Agsurf Industries",
  "company_logo_url": "http://127.0.0.1:8000/media/site/logo.png",
  "tagline": "Specialty Surfactants & Agrochemical Formulations",
  "about_us": "<p>Rich HTML about us content</p>",
  "vision": "<p>Vision statement HTML</p>",
  "mission": "<p>Mission statement HTML</p>",
  "manufacturing_expertise": "...",
  "rd_focus": "...",
  "sustainability": "...",
  "client_commitment": "...",
  "contact_email": "info@staragsurf.com",
  "contact_phone": "+91-XXXXXXXXXX",
  "contact_address": "Address here",
  "whatsapp_number": "+91-XXXXXXXXXX",
  "facebook_url": "",
  "linkedin_url": "",
  "instagram_url": "",
  "twitter_url": "",
  "youtube_url": "",
  "updated_at": "2026-06-15T16:07:51+05:30"
}
```

**Frontend usage:**
- Footer contact info
- About Us page (`about_us`, `vision`, `mission` as HTML)
- Header logo (`company_logo_url`)
- Social media links
- **Never hardcode company info** — always fetch from this endpoint

---

### 4.9 GET `/search/?q={query}`

Global search across products and categories.

**Query param:** `q` (min 2 characters)

**Response `200`:**

```json
{
  "query": "surfactant",
  "count": 15,
  "results": [
    {
      "type": "product",
      "id": 6,
      "name": "STAGSURF SC 6875",
      "slug": "stagsurf-sc-6875",
      "thumbnail_url": "...",
      "...": "full product card fields"
    },
    {
      "type": "category",
      "id": 2,
      "name": "SC Formulations",
      "slug": "sc-formulations",
      "description": "Suspension concentrate..."
    }
  ]
}
```

**Frontend usage:** Site-wide search dropdown / search results page.  
Route by `type`: `product` → `/products/{slug}`, `category` → `/categories/{slug}`.

---

### 4.10 POST `/inquiries/`

Submit a product or B2B inquiry.

**When to use:** Product page inquiry form, distributor/dealer interest.

**Request body:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+919876543210",
  "company": "Agri Distributors Ltd",
  "product_slug": "stagsurf-sc-6875",
  "source": "product_page",
  "message": "Interested in bulk supply for EC formulations."
}
```

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | Min 2 characters |
| `email` | Yes | Valid email |
| `phone` | Yes | 7–15 digits, optional `+` |
| `company` | No | — |
| `product_slug` | No | Must match a published product |
| `product_id` | No | Alternative to `product_slug` (use one, not both) |
| `source` | No | `website`, `product_page`, `contact_page` (default: `website`; auto `product_page` if product linked) |
| `message` | Yes | Min 10 characters |

**Response `201`:**

```json
{
  "success": true,
  "message": "Your inquiry has been submitted successfully.",
  "inquiry_id": 1,
  "product_id": 6,
  "product_name": "STAGSURF SC 6875"
}
```

**Response `400`:**

```json
{
  "success": false,
  "errors": {
    "email": ["Enter a valid email address."],
    "phone": ["Enter a valid phone number."]
  }
}
```

---

### 4.11 POST `/contact/`

Submit a general contact message (no product link).

**When to use:** Contact page, partnership inquiries without a specific product.

**Request body:**

```json
{
  "name": "Jane Smith",
  "email": "jane@company.com",
  "phone": "+919876543210",
  "subject": "Partnership Inquiry",
  "message": "We would like to discuss distribution partnership."
}
```

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | Min 2 characters |
| `email` | Yes | Valid email |
| `phone` | No | Valid format if provided |
| `subject` | Yes | Min 3 characters |
| `message` | Yes | Min 10 characters |

**Response `201`:**

```json
{
  "success": true,
  "message": "Your message has been sent successfully.",
  "contact_id": 1
}
```

---

## 5. Enums Reference

### Formulation Types (`formulation_type`)

| Value | Label |
|-------|-------|
| `SC` | SC Formulation |
| `EC` | EC Formulation |
| `ME` | ME Formulation |
| `EW` | EW Formulation |
| `ADJUVANT` | Adjuvant |
| `WETTING` | Wetting Agent |
| `DISPERSING` | Dispersing Agent |
| `TEXTILE` | Textile Chemical |
| `CROP_PROTECTION` | Crop Protection |
| `OTHER` | Other |

### Product Document Types

`TDS` | `BROCHURE` | `CATALOG` | `MSDS` | `PRODUCT_SHEET`

### Company Document Types

`COMPANY_PROFILE` | `COMPANY_BROCHURE` | `CERTIFICATE` | `TECHNICAL_CATALOG` | `OTHER`

### Inquiry Source

`website` | `product_page` | `contact_page`

---

## 6. Frontend Page → API Mapping

| Page | APIs to call |
|------|-------------|
| **Homepage** | `GET /site-settings/` + `GET /featured-products/` + `GET /categories/` |
| **Products listing** | `GET /products/` or `GET /products/?category={slug}` |
| **Product detail** | `GET /products/{slug}/` |
| **Category page** | `GET /categories/` + `GET /products/?category={slug}` |
| **About Us** | `GET /site-settings/` |
| **Contact page** | `GET /site-settings/` + `POST /contact/` |
| **Product inquiry form** | `POST /inquiries/` with `product_slug` |
| **Search results** | `GET /products/search/?q=` or `GET /search/?q=` |
| **Downloads / Resources** | `GET /company-documents/` + `GET /documents/` |
| **Footer** | `GET /site-settings/` |

---

## 7. React / Next.js Integration Examples

### Fetch helper

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Accept: "application/json" },
    next: { revalidate: 60 }, // ISR: refresh every 60s
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function apiPost<T>(path: string, body: object): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}
```

### Homepage

```typescript
const [settings, featured, categories] = await Promise.all([
  apiGet("/site-settings/"),
  apiGet("/featured-products/"),
  apiGet("/categories/"),
]);
```

### Product detail page (Next.js App Router)

```typescript
// app/products/[slug]/page.tsx
const product = await apiGet(`/products/${params.slug}/`);
```

### Submit inquiry form

```typescript
const result = await apiPost("/inquiries/", {
  name: form.name,
  email: form.email,
  phone: form.phone,
  company: form.company,
  product_slug: productSlug,
  source: "product_page",
  message: form.message,
});

if (result.success) {
  // show success message
} else {
  // show result.errors
}
```

### Render rich HTML from CMS

```tsx
<div dangerouslySetInnerHTML={{ __html: settings.about_us }} />
```

### Product card component

```tsx
<img src={product.thumbnail_url ?? "/placeholder.png"} alt={product.name} />
<Link href={`/products/${product.slug}`}>{product.name}</Link>
```

---

## 8. Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| `200` | Success | Use response data |
| `201` | Created (forms) | Show success message |
| `400` | Validation error | Show `errors` object field-by-field |
| `404` | Not found | Show "Product not found" page |
| `500` | Server error | Show generic error, retry |

**Validation error format (POST):**

```json
{
  "success": false,
  "errors": {
    "field_name": ["Error message"]
  }
}
```

---

## 9. Important Rules for Frontend Team

1. **Only published products** appear in API — draft/archived are hidden.
2. **Use `thumbnail_url`** for product cards, not gallery images.
3. **Use `file_url`** for PDF downloads — full absolute URL, use directly in `<a href>`.
4. **Render `description`, `about_us`, `vision`, `mission` as HTML** — they contain CKEditor markup.
5. **Do not hardcode** company name, contact, or product data.
6. **Inquiry vs Contact:** product-related → `/inquiries/`, general → `/contact/`.
7. **Sort order:** products already sorted by `display_order` from API.
8. **Pagination:** check `next` field for more pages on list endpoints.

---

## 10. Swagger / OpenAPI

Interactive API documentation is available when the backend server is running:

```powershell
python manage.py runserver
```

| Tool | URL |
|------|-----|
| **Swagger UI** | http://127.0.0.1:8000/api/docs/ |
| **ReDoc** | http://127.0.0.1:8000/api/redoc/ |
| **OpenAPI JSON** | http://127.0.0.1:8000/api/schema/ |

Use Swagger to test all endpoints live in the browser.

---

## 11. Local Setup (for frontend developers)

```powershell
# Backend must be running for API calls to work
cd "Star agro"
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Then point your frontend to: `http://127.0.0.1:8000/api/`

---

## 12. Support

| Question | Document |
|----------|----------|
| How does admin → frontend flow work? | [WORKFLOW.md](WORKFLOW.md) |
| Database schema & models? | [ARCHITECTURE.md](ARCHITECTURE.md) |
| API request/response details? | This file + Swagger |
| Backend setup? | [README.md](README.md) |

---

*Star Agsurf Industries — API Integration Guide v2.0*
