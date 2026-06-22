from django.core.management.base import BaseCommand
from django.db import connection, transaction

from apps.categories.models import Category
from apps.products.models import (
    Product,
    ProductApplication,
    ProductBenefit,
    ProductProperty,
)
from apps.site_settings.models import SiteSettings

from .seed_catalog import (
    CATEGORIES,
    LEGACY_CATEGORY_SLUGS,
    PRODUCT_TDS,
    PRODUCTS,
    SITE_SETTINGS,
    build_short_description,
)


class Command(BaseCommand):
    help = (
        "Load Star Agsurf categories, products, and site settings. "
        "Use --dry-run to validate without writing to the database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate catalog data and DB connectivity without writing.",
        )
        parser.add_argument(
            "--skip-site-settings",
            action="store_true",
            help="Skip updating site settings.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        skip_site_settings = options["skip_site_settings"]

        errors = self._validate_catalog()
        if errors:
            for error in errors:
                self.stdout.write(self.style.ERROR(error))
            raise SystemExit(1)

        self._print_summary(dry_run)

        if dry_run:
            self._check_db_connection()
            self.stdout.write(self.style.SUCCESS("Dry run passed — no data was written."))
            return

        with transaction.atomic():
            if not skip_site_settings:
                SiteSettings.objects.update_or_create(pk=1, defaults=SITE_SETTINGS)

            category_map = {}
            for name, slug, description, display_order in CATEGORIES:
                cat, _ = Category.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "description": description,
                        "display_order": display_order,
                        "is_active": True,
                    },
                )
                category_map[slug] = cat

            Category.objects.filter(slug__in=LEGACY_CATEGORY_SLUGS).update(is_active=False)

            seed_slugs = set()
            for i, row in enumerate(PRODUCTS):
                (
                    name,
                    slug,
                    cat_slug,
                    form_type,
                    code,
                    equivalent,
                    function,
                    formulation,
                    is_featured,
                ) = row
                seed_slugs.add(slug)

                product, _ = Product.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "product_code": code,
                        "category": category_map[cat_slug],
                        "formulation_type": form_type,
                        "short_description": build_short_description(
                            name, function, equivalent, formulation
                        ),
                        "is_featured": is_featured,
                        "display_order": i,
                        "status": Product.Status.PUBLISHED,
                    },
                )
                self._apply_tds(product, slug)

            Product.objects.exclude(slug__in=seed_slugs).update(status=Product.Status.ARCHIVED)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(CATEGORIES)} categories and {len(PRODUCTS)} products successfully."
            )
        )

    def _validate_catalog(self):
        errors = []
        category_slugs = [slug for _, slug, _, _ in CATEGORIES]
        if len(category_slugs) != len(set(category_slugs)):
            errors.append("Duplicate category slugs found in catalog data.")

        product_slugs = [row[1] for row in PRODUCTS]
        if len(product_slugs) != len(set(product_slugs)):
            dupes = sorted({s for s in product_slugs if product_slugs.count(s) > 1})
            errors.append(f"Duplicate product slugs found: {', '.join(dupes)}")

        category_slug_set = set(category_slugs)
        valid_form_types = {choice[0] for choice in Product.FormulationType.choices}

        for row in PRODUCTS:
            name, slug, cat_slug, form_type, *_ = row
            if cat_slug not in category_slug_set:
                errors.append(f"Product '{name}' references unknown category '{cat_slug}'.")
            if form_type not in valid_form_types:
                errors.append(
                    f"Product '{name}' has invalid formulation_type '{form_type}'."
                )

        for slug in PRODUCT_TDS:
            if slug not in product_slugs:
                errors.append(f"TDS entry references unknown product slug '{slug}'.")

        return errors

    def _print_summary(self, dry_run):
        mode = "DRY RUN" if dry_run else "LIVE SEED"
        self.stdout.write(self.style.WARNING(f"=== {mode} ==="))
        self.stdout.write(f"Categories: {len(CATEGORIES)}")
        self.stdout.write(f"Products:   {len(PRODUCTS)}")
        self.stdout.write(f"TDS detail: {len(PRODUCT_TDS)} products")
        self.stdout.write("")
        for name, slug, _, _ in CATEGORIES:
            count = sum(1 for row in PRODUCTS if row[2] == slug)
            self.stdout.write(f"  [{count:2d}] {name}")

    def _check_db_connection(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_name = connection.settings_dict.get("NAME", "unknown")
            db_host = connection.settings_dict.get("HOST", "localhost")
            self.stdout.write(
                self.style.SUCCESS(f"Database connection OK — {db_name} @ {db_host}")
            )
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Database connection failed: {exc}"))
            raise SystemExit(1) from exc

    def _apply_tds(self, product, slug):
        tds = PRODUCT_TDS.get(slug)
        if not tds:
            return

        if tds.get("description"):
            product.description = tds["description"]
            product.save(update_fields=["description"])

        for j, (prop_name, prop_value) in enumerate(tds.get("properties", [])):
            ProductProperty.objects.update_or_create(
                product=product,
                property_name=prop_name,
                defaults={"property_value": prop_value, "display_order": j},
            )

        for j, benefit in enumerate(tds.get("benefits", [])):
            ProductBenefit.objects.update_or_create(
                product=product,
                benefit=benefit,
                defaults={"display_order": j},
            )

        for j, app_text in enumerate(tds.get("applications", [])):
            ProductApplication.objects.update_or_create(
                product=product,
                application_text=app_text,
                defaults={"display_order": j},
            )
