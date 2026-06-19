# Star Agsurf — Frontend API Integration

> Share this file with the frontend team and open it in Cursor.  
> **Base URL:** `https://star-api.aspune.cloud/api`

---

## Cursor Prompt (copy & paste in frontend folder)

Use this in your **frontend project** when UI is already done and you only need API integration:

```
Read FRONTEND_INTEGRATION.md in this project.

The UI/design is already complete. Do NOT change layout, styling, or page structure.

Your job is ONLY to connect the existing pages/components to the backend API:
- Base URL: https://star-api.aspune.cloud/api
- Replace all hardcoded/mock/static product, category, about, contact, logo, and document data with live API calls from this document.
- Wire forms: product inquiry → POST /inquiries/, contact page → POST /contact/
- Use the "Which API for Which Page" table to map each existing page to the correct endpoint.
- Admin adds/edits content in Django Admin → frontend must read it via GET APIs (no admin login in frontend).
- Only published products appear in API. Use thumbnail_url, file_url, image_url from API responses.
- Render description, about_us, vision, mission as HTML from API.
- Add NEXT_PUBLIC_API_BASE_URL=https://star-api.aspune.cloud/api in .env
- Keep existing component names and UI. Only add API fetch logic, env config, and connect props/state to API data.
```

---

## How Admin Panel Connects to Frontend

**Frontend does NOT connect to admin panel directly.**  
Admin and frontend both use the same backend database — admin writes, frontend reads.

```
ADMIN (Django Admin)                    FRONTEND (Website)
https://star-api.aspune.cloud/admin/    https://your-frontend-domain.com

Admin adds/edits:                       Frontend reads via API:
├── Products                            ├── GET /products/
├── Categories                          ├── GET /categories/
├── Product images, specs, PDFs         ├── GET /products/{slug}/
├── Site settings (logo, about, contact)├── GET /site-settings/
├── Company documents                   ├── GET /company-documents/
└── Featured flag on products           └── GET /featured-products/

Visitor submits form on website  →  POST /inquiries/ or POST /contact/  →  Admin sees it in Admin panel
```

### Important rules

| Admin action | What frontend shows |
|--------------|----------------------|
| Admin adds product + sets status **Published** | Product appears in `GET /products/` and detail page |
| Admin sets product as **Draft** or **Archived** | Product **hidden** from frontend (404 on detail) |
| Admin marks product **Featured** | Shows in `GET /featured-products/` (homepage) |
| Admin uploads product image / thumbnail | Shows in `thumbnail_url` and `images[]` on product page |
| Admin uploads PDF (TDS, brochure) | Shows in `documents[]` or `GET /documents/` |
| Admin edits About Us / Vision / Mission | Updates on About page via `GET /site-settings/` |
| Admin changes logo, phone, email, address | Updates header/footer via `GET /site-settings/` |
| Admin adds category | Shows in nav + category filter via `GET /categories/` |
| Visitor submits inquiry on product page | Saved in Admin → Inquiries (frontend sends `POST /inquiries/`) |
| Visitor submits contact form | Saved in Admin → Contact Messages (frontend sends `POST /contact/`) |

**No frontend code needed for admin.** Admin team manages everything from Django Admin. Frontend only calls GET APIs to display data and POST APIs for forms.

---

## How It Works

```
Frontend  ──GET──►  /api/*          → read products, categories, CMS, documents
Frontend  ──POST──► /api/inquiries/ → product inquiry form
Frontend  ──POST──► /api/contact/   → general contact form
```

- **No login / no token** required for any public API.
- **All content** (products, about us, contact info, logo) comes from API — do not hardcode.
- Admin updates content in Django Admin → frontend sees changes on **next page load / API call**.
- Only **published** products are returned.
- **Frontend never talks to admin panel** — only to `/api/*` endpoints.

---

## Setup

### Environment variable

```env
NEXT_PUBLIC_API_BASE_URL=https://star-api.aspune.cloud/api
```

### Headers (all requests)

```http
Accept: application/json
Content-Type: application/json    ← POST only
```

### CORS

The backend allows browser requests from:

- `http://localhost:*` and `http://127.0.0.1:*` (any dev port)
- `https://*.aspune.cloud`
- `https://staragsurf.com` and `https://www.staragsurf.com`
- Any origin listed in server env `CORS_ALLOWED_ORIGINS`

If the contact form shows a CORS error, confirm the frontend domain is covered above or ask backend to add it to `CORS_ALLOWED_ORIGINS`.

### Pagination

List endpoints return:

```json
{
  "count": 18,
  "next": "https://star-api.aspune.cloud/api/products/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

- **20 items per page**
- Use `next` URL or `?page=2` for more results

---

## All APIs

| # | Method | Endpoint | Purpose |
|---|--------|----------|---------|
| 1 | GET | `/categories/` | Category list |
| 2 | GET | `/products/` | Product list (filterable) |
| 3 | GET | `/products/{slug}/` | Product detail |
| 4 | GET | `/featured-products/` | Featured products |
| 5 | GET | `/products/search/?q=` | Search products |
| 6 | GET | `/documents/` | Product PDFs |
| 7 | GET | `/company-documents/` | Company PDFs |
| 8 | GET | `/site-settings/` | Logo, about, contact, social |
| 9 | GET | `/search/?q=` | Global search |
| 10 | POST | `/inquiries/` | Product inquiry form |
| 11 | GET | `/contact/reasons/` | Contact form reason dropdown options |
| 12 | POST | `/contact/` | Contact form |

**Live docs:** https://star-api.aspune.cloud/api/docs/

---

## 1. GET `/categories/`

**Use for:** navigation menu, category filters

```json
{
  "count": 9,
  "results": [
    {
      "id": 1,
      "name": "SC Formulations",
      "slug": "sc-formulations",
      "description": "...",
      "image": null,
      "display_order": 1,
      "meta_title": "",
      "meta_description": "",
      "product_count": 7
    }
  ]
}
```

---

## 2. GET `/products/`

**Use for:** product listing, category pages

**Filters:**

| Param | Example | Description |
|-------|---------|-------------|
| `category` | `sc-formulations` | Category slug |
| `formulation_type` | `SC` | Formulation type |
| `formulation` | `EC` | Same as `formulation_type` |
| `product_type` | `adjuvants` | Formulation or category slug |
| `featured` | `true` | Featured only |
| `page` | `2` | Pagination |

**Example:** `GET /api/products/?category=sc-formulations`

```json
{
  "count": 7,
  "results": [
    {
      "id": 6,
      "name": "STAGSURF SC 6875",
      "slug": "stagsurf-sc-6875",
      "product_code": "STAGSURF SC 6875",
      "short_description": "...",
      "category_name": "SC Formulations",
      "category_slug": "sc-formulations",
      "formulation_type": "SC",
      "is_featured": false,
      "display_order": 5,
      "meta_title": "",
      "meta_description": "",
      "thumbnail_url": "https://star-api.aspune.cloud/media/products/thumbnails/image.jpg"
    }
  ]
}
```

> Use `thumbnail_url` for product cards. If `null`, show a placeholder.

---

## 3. GET `/products/{slug}/`

**Use for:** product detail page

**Example:** `GET /api/products/stagsurf-sc-6875/`

```json
{
  "id": 6,
  "name": "STAGSURF SC 6875",
  "slug": "stagsurf-sc-6875",
  "product_code": "STAGSURF SC 6875",
  "short_description": "...",
  "description": "<p>HTML content from admin</p>",
  "technical_specifications": "...",
  "formulation_type": "SC",
  "is_featured": false,
  "display_order": 5,
  "thumbnail_url": "https://star-api.aspune.cloud/media/...",
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
      "image_url": "https://star-api.aspune.cloud/media/products/images/photo1.jpg",
      "alt_text": "Product photo",
      "is_primary": true,
      "display_order": 0
    }
  ],
  "properties": [
    { "id": 1, "property_name": "Appearance", "property_value": "Pale Yellow Liquid", "display_order": 0 }
  ],
  "benefits": [
    { "id": 1, "benefit": "Increases herbicide penetration", "display_order": 0 }
  ],
  "applications": [
    { "id": 1, "application_text": "Crop Protection", "display_order": 0 }
  ],
  "documents": [
    {
      "id": 1,
      "document_name": "STAGSURF SC 6875 TDS",
      "document_type": "TDS",
      "file_url": "https://star-api.aspune.cloud/media/documents/products/tds.pdf",
      "display_order": 0
    }
  ],
  "meta_title": "",
  "meta_description": "",
  "created_at": "2026-06-15T16:07:51+05:30",
  "updated_at": "2026-06-15T16:13:45+05:30"
}
```

- `description` → render as HTML
- `properties` → specs table
- `benefits` → bullet list
- `applications` → tags
- `documents[].file_url` → download link
- **404** if product not found or not published

---

## 4. GET `/featured-products/`

Same response shape as `/products/` — only products where `is_featured = true`.

**Use for:** homepage featured section.

---

## 5. GET `/products/search/?q={query}`

**Use for:** product search

- `q` is **required**, minimum **2 characters**
- Same filters as `/products/` (`category`, `formulation_type`, etc.)

**Example:** `GET /api/products/search/?q=stagsurf`

```json
{
  "query": "stagsurf",
  "count": 12,
  "results": [ /* same as product list */ ]
}
```

**400 error:**

```json
{ "detail": "Search query must be at least 2 characters." }
```

---

## 6. GET `/documents/`

**Use for:** downloads page — product PDFs

| Param | Example |
|-------|---------|
| `type` | `TDS` |
| `product` | `stagsurf-sc-6875` |

**Types:** `TDS`, `BROCHURE`, `CATALOG`, `MSDS`, `PRODUCT_SHEET`

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "document_name": "STAGSURF SC 6875 TDS",
      "document_type": "TDS",
      "file_url": "https://star-api.aspune.cloud/media/documents/products/tds.pdf",
      "product_name": "STAGSURF SC 6875",
      "product_slug": "stagsurf-sc-6875",
      "display_order": 0,
      "created_at": "2026-06-15T16:07:51+05:30"
    }
  ]
}
```

---

## 7. GET `/company-documents/`

**Use for:** company profile, brochures, certificates

| Param | Example |
|-------|---------|
| `type` | `COMPANY_PROFILE` |

**Types:** `COMPANY_PROFILE`, `COMPANY_BROCHURE`, `CERTIFICATE`, `TECHNICAL_CATALOG`, `OTHER`

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "title": "Company Profile 2026",
      "document_type": "COMPANY_PROFILE",
      "file_url": "https://star-api.aspune.cloud/media/documents/company/profile.pdf",
      "display_order": 0,
      "created_at": "2026-06-15T16:07:51+05:30"
    }
  ]
}
```

---

## 8. GET `/site-settings/`

**Use for:** header logo, footer contact, about us page, social links

```json
{
  "site_name": "Star Agsurf Industries",
  "company_logo_url": "https://star-api.aspune.cloud/media/site/logo.png",
  "tagline": "Specialty Surfactants & Agrochemical Formulations",
  "about_us": "<p>HTML content</p>",
  "vision": "<p>HTML content</p>",
  "mission": "<p>HTML content</p>",
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

- `about_us`, `vision`, `mission` → render as HTML
- Hide social icon if URL is empty

---

## 9. GET `/search/?q={query}`

**Use for:** site-wide search (products + categories)

- `q` minimum **2 characters**

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
      "thumbnail_url": "..."
    },
    {
      "type": "category",
      "id": 2,
      "name": "SC Formulations",
      "slug": "sc-formulations",
      "description": "..."
    }
  ]
}
```

- `type: "product"` → link to `/products/{slug}`
- `type: "category"` → link to products filtered by category

---

## 10. POST `/inquiries/`

**Use for:** product page inquiry form, B2B / distributor interest

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

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | Min 2 chars |
| `email` | Yes | Valid email |
| `phone` | Yes | 7–15 digits, optional `+` |
| `company` | No | — |
| `product_slug` | No | Must be a published product |
| `product_id` | No | Use instead of slug (not both) |
| `source` | No | `website`, `product_page`, `contact_page` |
| `message` | Yes | Min 10 chars |

**Success `201`:**

```json
{
  "success": true,
  "message": "Your inquiry has been submitted successfully.",
  "inquiry_id": 1,
  "product_id": 6,
  "product_name": "STAGSURF SC 6875"
}
```

**Error `400`:**

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

## 11. GET `/contact/reasons/`

**Use for:** contact page — populate the "Reason for Contact" dropdown

**Response `200`:**

```json
[
  { "value": "general_inquiry", "label": "General Inquiry" },
  { "value": "product_information", "label": "Product Information" },
  { "value": "product_specific_inquiry", "label": "Product Specific Inquiry" },
  { "value": "technical_support", "label": "Technical Support" },
  { "value": "dealer_inquiry", "label": "Dealer Inquiry" },
  { "value": "distributor_inquiry", "label": "Distributor Inquiry" },
  { "value": "sample_request", "label": "Sample Request" },
  { "value": "pricing_quotation", "label": "Pricing & Quotation" },
  { "value": "partnership_opportunity", "label": "Partnership Opportunity" },
  { "value": "other", "label": "Other" }
]
```

You can hardcode these in the frontend UI, or fetch them from this endpoint so admin/backend stays the source of truth.

---

## 12. POST `/contact/`

**Use for:** contact page — general messages (no product link)

**Request:**

```json
{
  "name": "Jane Smith",
  "email": "jane@company.com",
  "phone": "+919876543210",
  "reason": "partnership_opportunity",
  "message": "We would like to discuss distribution."
}
```

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | Min 2 chars |
| `email` | Yes | Valid email |
| `phone` | No | Valid format if provided |
| `reason` | Yes | One of the values from `GET /contact/reasons/` (or send the label e.g. `"General Inquiry"`) |
| `subject` | No | Alias for `reason` (backward compatible) |
| `message` | Yes | Min 10 chars |

**Success `201`:**

```json
{
  "success": true,
  "message": "Your message has been sent successfully.",
  "contact_id": 1
}
```

---

## Which API for Which Page

| Page | API to call |
|------|-------------|
| Header / Footer | `GET /site-settings/` + `GET /categories/` |
| Homepage | `GET /site-settings/` + `GET /featured-products/` + `GET /categories/` |
| Products list | `GET /products/` |
| Product detail | `GET /products/{slug}/` |
| Category page | `GET /products/?category={slug}` |
| About Us | `GET /site-settings/` |
| Contact page | `GET /site-settings/` + `GET /contact/reasons/` + `POST /contact/` |
| Product inquiry | `POST /inquiries/` with `product_slug` |
| Search | `GET /search/?q=` or `GET /products/search/?q=` |
| Downloads | `GET /company-documents/` + `GET /documents/` |

---

## Integration Example

```javascript
const API = process.env.NEXT_PUBLIC_API_BASE_URL; // https://star-api.aspune.cloud/api

// GET
async function getProducts(category) {
  const url = category
    ? `${API}/products/?category=${category}`
    : `${API}/products/`;
  const res = await fetch(url, { headers: { Accept: "application/json" } });
  return res.json();
}

// POST inquiry
async function submitInquiry(data) {
  const res = await fetch(`${API}/inquiries/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// GET contact reasons (optional — can hardcode dropdown from section 11)
async function getContactReasons() {
  const res = await fetch(`${API}/contact/reasons/`, {
    headers: { Accept: "application/json" },
  });
  return res.json();
}

// POST contact form
async function submitContact(data) {
  const res = await fetch(`${API}/contact/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      name: data.name,
      email: data.email,
      phone: data.phone,
      reason: data.reason, // e.g. "general_inquiry" or "General Inquiry"
      message: data.message,
    }),
  });
  return res.json();
}
```

---

## Important Rules

1. **Inquiry** (`POST /inquiries/`) → when user asks about a specific product  
2. **Contact** (`POST /contact/`) → general messages, no product  
3. Use **`thumbnail_url`** on cards, **`file_url`** for PDFs, **`image_url`** for gallery  
4. Render **`description`**, **`about_us`**, **`vision`**, **`mission`** as HTML  
5. SEO: use `meta_title` / `meta_description` from API; fallback to `name` / `short_description`  
6. Search: wait until user types **2+ characters** before calling API

---

## Error Codes

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `201` | Form submitted |
| `400` | Validation error — show `errors` field messages |
| `404` | Not found |
| `500` | Server error — retry |

---

## Quick Checklist — Is Everything Covered?

| Topic | Covered in this doc? |
|-------|----------------------|
| Deploy API base URL | Yes — `https://star-api.aspune.cloud/api` |
| All 12 API endpoints | Yes — with request/response examples |
| Which API for each page | Yes — table above |
| Admin adds product → shows on website | Yes — Published status required |
| Admin edits About/Contact/Logo | Yes — via `GET /site-settings/` |
| Admin uploads PDFs | Yes — `GET /documents/` + `GET /company-documents/` |
| Inquiry form → admin panel | Yes — `POST /inquiries/` |
| Contact form → admin panel | Yes — `POST /contact/` |
| Search, filters, pagination | Yes |
| No auth / no admin login in frontend | Yes |
| Cursor prompt for existing UI | Yes — top of this file |
| Live Swagger docs | Yes — https://star-api.aspune.cloud/api/docs/ |

**Not in frontend scope:** Django Admin login, database, backend setup — admin team handles that separately.

---

*Star Agsurf Industries — API Integration Guide*
