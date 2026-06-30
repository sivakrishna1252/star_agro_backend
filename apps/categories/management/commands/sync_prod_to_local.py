"""
Copy categories and products from production DB into the local default DB.

Production connection is READ-ONLY. Local DB is the only write target.
"""

import os

import psycopg2
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.categories.models import Category
from apps.products.models import (
    Product,
    ProductApplication,
    ProductBenefit,
    ProductProperty,
)


PROD_DB = {
    "host": os.getenv("PROD_DB_HOST", "72.60.219.145"),
    "port": int(os.getenv("PROD_DB_PORT", "5432")),
    "dbname": os.getenv("PROD_DB_NAME", "star_agro"),
    "user": os.getenv("PROD_DB_USER", "aspl"),
    "password": os.getenv("PROD_DB_PASSWORD", "ASPune$2210$"),
}


class Command(BaseCommand):
    help = (
        "Copy categories and products from production into local DB. "
        "Production is read-only; only local DB is modified."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show production counts and planned sync without writing locally.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        local_db = settings.DATABASES["default"]

        self.stdout.write(
            self.style.WARNING(
                f"Production (read-only): {PROD_DB['dbname']} @ {PROD_DB['host']}"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f"Local (write target):   {local_db['NAME']} @ {local_db['HOST']}"
            )
        )

        if local_db["HOST"] not in ("127.0.0.1", "localhost"):
            raise SystemExit(
                "Refusing to write: default DB host is not local. "
                "Point .env DB_HOST to 127.0.0.1 before syncing."
            )

        prod_conn = psycopg2.connect(**PROD_DB)
        prod_conn.set_session(readonly=True, autocommit=True)

        try:
            categories = self._fetch_categories(prod_conn)
            products = self._fetch_products(prod_conn)
            properties = self._fetch_properties(prod_conn)
            benefits = self._fetch_benefits(prod_conn)
            applications = self._fetch_applications(prod_conn)
        finally:
            prod_conn.close()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== PRODUCTION (read-only) ==="))
        self.stdout.write(f"Categories (active): {sum(1 for c in categories if c['is_active'])}")
        self.stdout.write(f"Categories (total):    {len(categories)}")
        self.stdout.write(f"Products (published): {sum(1 for p in products if p['status'] == 'published')}")
        self.stdout.write(f"Products (total):      {len(products)}")

        self.stdout.write("")
        self.stdout.write("=== LOCAL (before) ===")
        self.stdout.write(f"Categories (active): {Category.objects.filter(is_active=True).count()}")
        self.stdout.write(f"Categories (total):    {Category.objects.count()}")
        self.stdout.write(f"Products (published): {Product.objects.published().count()}")
        self.stdout.write(f"Products (total):      {Product.objects.count()}")

        if dry_run:
            self.stdout.write(self.style.SUCCESS("Dry run complete — local DB unchanged."))
            return

        with transaction.atomic():
            ProductProperty.objects.all().delete()
            ProductBenefit.objects.all().delete()
            ProductApplication.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()

            category_map = {}
            for row in categories:
                cat = Category.objects.create(
                    name=row["name"],
                    slug=row["slug"],
                    description=row["description"] or "",
                    is_active=row["is_active"],
                    display_order=row["display_order"],
                    meta_title=row["meta_title"] or "",
                    meta_description=row["meta_description"] or "",
                )
                category_map[row["slug"]] = cat

            product_map = {}
            for row in products:
                cat_slug = row["category_slug"]
                if cat_slug not in category_map:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping product '{row['name']}' — missing category '{cat_slug}'."
                        )
                    )
                    continue

                product = Product.objects.create(
                    category=category_map[cat_slug],
                    name=row["name"],
                    slug=row["slug"],
                    product_code=row["product_code"] or "",
                    short_description=row["short_description"] or "",
                    description=row["description"] or "",
                    technical_specifications=row["technical_specifications"] or "",
                    formulation_type=row["formulation_type"],
                    status=row["status"],
                    is_featured=row["is_featured"],
                    display_order=row["display_order"],
                    meta_title=row["meta_title"] or "",
                    meta_description=row["meta_description"] or "",
                )
                product_map[row["slug"]] = product

            for row in properties:
                product = product_map.get(row["product_slug"])
                if product:
                    ProductProperty.objects.create(
                        product=product,
                        property_name=row["property_name"],
                        property_value=row["property_value"],
                        display_order=row["display_order"],
                    )

            for row in benefits:
                product = product_map.get(row["product_slug"])
                if product:
                    ProductBenefit.objects.create(
                        product=product,
                        benefit=row["benefit"],
                        display_order=row["display_order"],
                    )

            for row in applications:
                product = product_map.get(row["product_slug"])
                if product:
                    ProductApplication.objects.create(
                        product=product,
                        application_text=row["application_text"],
                        display_order=row["display_order"],
                    )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== LOCAL (after sync) ==="))
        self.stdout.write(f"Categories (active): {Category.objects.filter(is_active=True).count()}")
        self.stdout.write(f"Categories (total):    {Category.objects.count()}")
        self.stdout.write(f"Products (published): {Product.objects.published().count()}")
        self.stdout.write(f"Products (total):      {Product.objects.count()}")
        self.stdout.write(
            self.style.SUCCESS(
                "Sync complete — production DB was not modified."
            )
        )

    def _fetch_categories(self, conn):
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT name, slug, description, is_active, display_order,
                       meta_title, meta_description
                FROM categories_category
                ORDER BY display_order, name
                """
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def _fetch_products(self, conn):
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.name, p.slug, p.product_code, p.short_description,
                       p.description, p.technical_specifications,
                       p.formulation_type, p.status, p.is_featured,
                       p.display_order, p.meta_title, p.meta_description,
                       c.slug AS category_slug
                FROM products_product p
                JOIN categories_category c ON c.id = p.category_id
                ORDER BY p.display_order, p.name
                """
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def _fetch_properties(self, conn):
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.slug AS product_slug, pp.property_name,
                       pp.property_value, pp.display_order
                FROM products_productproperty pp
                JOIN products_product p ON p.id = pp.product_id
                ORDER BY pp.display_order, pp.property_name
                """
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def _fetch_benefits(self, conn):
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.slug AS product_slug, pb.benefit, pb.display_order
                FROM products_productbenefit pb
                JOIN products_product p ON p.id = pb.product_id
                ORDER BY pb.display_order, pb.id
                """
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def _fetch_applications(self, conn):
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.slug AS product_slug, pa.application_text, pa.display_order
                FROM products_productapplication pa
                JOIN products_product p ON p.id = pa.product_id
                ORDER BY pa.display_order, pa.id
                """
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
