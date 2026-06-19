from django.urls import path

from api.views.categories import CategoryListView
from api.views.company_documents import CompanyDocumentListView
from api.views.contact import ContactCreateView, ContactReasonListView
from api.views.documents import DocumentListView
from api.views.inquiries import InquiryCreateView
from api.views.products import (
    FeaturedProductListView,
    ProductDetailView,
    ProductListView,
    ProductSearchView,
)
from api.views.search import SearchView
from api.views.site_settings import SiteSettingsView

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/search/", ProductSearchView.as_view(), name="product-search"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("featured-products/", FeaturedProductListView.as_view(), name="featured-products"),
    path("documents/", DocumentListView.as_view(), name="document-list"),
    path("company-documents/", CompanyDocumentListView.as_view(), name="company-documents"),
    path("inquiries/", InquiryCreateView.as_view(), name="inquiry-create"),
    path("contact/reasons/", ContactReasonListView.as_view(), name="contact-reasons"),
    path("contact/", ContactCreateView.as_view(), name="contact-create"),
    path("site-settings/", SiteSettingsView.as_view(), name="site-settings"),
    path("search/", SearchView.as_view(), name="search"),
]
