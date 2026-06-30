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
    BROCHURE_COMPARISON_SLUGS,
    BROCHURE_PRODUCT_SLUGS,
    BROCHURE_SPECIALTY_SLUGS,
    CATEGORIES,
    CLIENT_REMOVED_PRODUCT_SLUGS,
    LEGACY_CATEGORY_SLUGS,
    PRODUCT_TDS,
    PRODUCTS,
    SITE_SETTINGS,
    build_short_description,
    catalog_products,
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
        parser.add_argument(
            "--brochure-comparison-only",
            action="store_true",
            help=(
                "Seed only brochure pages 4–5 product comparison data. "
                "Skips site settings and does not archive other products."
            ),
        )
        parser.add_argument(
            "--brochure-specialty-only",
            action="store_true",
            help=(
                "Seed only brochure page 3 specialty products. "
                "Skips site settings and does not archive other products."
            ),
        )
        parser.add_argument(
            "--brochure-products-only",
            action="store_true",
            help=(
                "Seed all brochure product pages (3, 4, and 5). "
                "Skips site settings and does not archive other products."
            ),
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        skip_site_settings = options["skip_site_settings"]
        seed_scope = self._resolve_seed_scope(options)

        if seed_scope != "full":
            skip_site_settings = True

        product_rows = self._product_rows(seed_scope)
        errors = self._validate_catalog(product_rows, seed_scope)
        if errors:
            for error in errors:
                self.stdout.write(self.style.ERROR(error))
            raise SystemExit(1)

        self._print_summary(dry_run, product_rows, seed_scope)

        if dry_run:
            self._check_db_connection()
            self.stdout.write(self.style.SUCCESS("Dry run passed — no data was written."))
            return

        with transaction.atomic():
            if not skip_site_settings:
                SiteSettings.objects.update_or_create(pk=1, defaults=SITE_SETTINGS)

            category_map = {}
            category_rows = self._category_rows(seed_scope)
            for name, slug, description, display_order in category_rows:
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

            if seed_scope == "full":
                Category.objects.filter(slug__in=LEGACY_CATEGORY_SLUGS).update(is_active=False)
            elif seed_scope == "brochure":
                brochure_cat_slugs = {row[1] for row in category_rows}
                Category.objects.filter(slug__in=LEGACY_CATEGORY_SLUGS).update(is_active=False)
                Category.objects.exclude(slug__in=brochure_cat_slugs).filter(
                    products__isnull=True
                ).update(is_active=False)

            seed_slugs = set()
            for i, row in enumerate(product_rows):
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
                self._apply_comparison_fields(product, equivalent, function, formulation)
                self._apply_tds(product, slug)

            if seed_scope == "full":
                Product.objects.exclude(slug__in=seed_slugs).update(status=Product.Status.ARCHIVED)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(category_rows)} categories and {len(product_rows)} "
                f"products ({self._scope_label(seed_scope)}) successfully."
            )
        )

    def _resolve_seed_scope(self, options):
        flags = [
            options["brochure_comparison_only"],
            options["brochure_specialty_only"],
            options["brochure_products_only"],
        ]
        if sum(flags) > 1:
            raise SystemExit(
                "Use only one brochure seed flag: "
                "--brochure-comparison-only, --brochure-specialty-only, "
                "or --brochure-products-only."
            )
        if options["brochure_comparison_only"]:
            return "comparison"
        if options["brochure_specialty_only"]:
            return "specialty"
        if options["brochure_products_only"]:
            return "brochure"
        return "full"

    def _brochure_slugs(self, seed_scope):
        if seed_scope == "comparison":
            return BROCHURE_COMPARISON_SLUGS
        if seed_scope == "specialty":
            return BROCHURE_SPECIALTY_SLUGS
        if seed_scope == "brochure":
            return BROCHURE_PRODUCT_SLUGS
        return None

    def _product_rows(self, seed_scope):
        slugs = self._brochure_slugs(seed_scope)
        if slugs is None:
            return catalog_products()
        return [row for row in catalog_products() if row[1] in slugs]

    def _category_rows(self, seed_scope):
        if seed_scope == "full":
            return CATEGORIES
        needed = {row[2] for row in self._product_rows(seed_scope)}
        return [row for row in CATEGORIES if row[1] in needed]

    def _scope_label(self, seed_scope):
        return {
            "full": "full catalog",
            "comparison": "brochure pages 4–5",
            "specialty": "brochure page 3 specialty",
            "brochure": "brochure pages 3, 4, and 5",
        }[seed_scope]

    def _validate_catalog(self, product_rows, seed_scope):
        errors = []
        category_rows = self._category_rows(seed_scope)
        category_slugs = [slug for _, slug, _, _ in category_rows]
        if len(category_slugs) != len(set(category_slugs)):
            errors.append("Duplicate category slugs found in catalog data.")

        product_slugs = [row[1] for row in product_rows]
        if len(product_slugs) != len(set(product_slugs)):
            dupes = sorted({s for s in product_slugs if product_slugs.count(s) > 1})
            errors.append(f"Duplicate product slugs found: {', '.join(dupes)}")

        category_slug_set = set(category_slugs)
        valid_form_types = {choice[0] for choice in Product.FormulationType.choices}

        for row in product_rows:
            name, slug, cat_slug, form_type, *_ = row
            if cat_slug not in category_slug_set:
                errors.append(f"Product '{name}' references unknown category '{cat_slug}'.")
            if form_type not in valid_form_types:
                errors.append(
                    f"Product '{name}' has invalid formulation_type '{form_type}'."
                )

        if seed_scope == "full":
            all_product_slugs = [row[1] for row in catalog_products()]
            for slug in PRODUCT_TDS:
                if slug not in all_product_slugs:
                    errors.append(f"TDS entry references unknown product slug '{slug}'.")

        brochure_slugs = self._brochure_slugs(seed_scope)
        if brochure_slugs is not None:
            missing = brochure_slugs - set(product_slugs)
            if missing:
                errors.append(
                    f"Brochure slugs missing from catalog: {', '.join(sorted(missing))}"
                )

        return errors

    def _print_summary(self, dry_run, product_rows, seed_scope):
        category_rows = self._category_rows(seed_scope)
        mode = "DRY RUN" if dry_run else "LIVE SEED"
        scope = self._scope_label(seed_scope).upper()
        self.stdout.write(self.style.WARNING(f"=== {mode} — {scope} ==="))
        self.stdout.write(f"Categories: {len(category_rows)}")
        self.stdout.write(f"Products:   {len(product_rows)}")
        if seed_scope == "full":
            self.stdout.write(f"TDS detail: {len(PRODUCT_TDS)} products")
        self.stdout.write("")
        for name, slug, _, _ in category_rows:
            count = sum(1 for row in product_rows if row[2] == slug)
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

    def _apply_comparison_fields(self, product, equivalent, function, formulation):
        """Map brochure product lines to structured product fields."""
        ProductProperty.objects.update_or_create(
            product=product,
            property_name="Function",
            defaults={"property_value": function, "display_order": 0},
        )
        if equivalent:
            ProductProperty.objects.update_or_create(
                product=product,
                property_name="Equivalent Product",
                defaults={"property_value": equivalent, "display_order": 1},
            )

        formulation_parts = [
            part.strip() for part in formulation.replace(";", ",").split(",") if part.strip()
        ]
        for j, app_text in enumerate(formulation_parts):
            ProductApplication.objects.update_or_create(
                product=product,
                application_text=app_text,
                defaults={"display_order": j},
            )

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
