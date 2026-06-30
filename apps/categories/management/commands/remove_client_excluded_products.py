"""Remove client-excluded brochure comparison products from the database."""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.categories.models import Category
from apps.products.models import Product

from .seed_catalog import CLIENT_REMOVED_PRODUCT_SLUGS


class Command(BaseCommand):
    help = (
        "Delete client-excluded products (3 removed brochure tables) and "
        "deactivate categories that become empty."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without writing.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        db = settings.DATABASES["default"]
        self.stdout.write(f"Database: {db['NAME']} @ {db['HOST']}")

        to_remove = Product.objects.filter(slug__in=CLIENT_REMOVED_PRODUCT_SLUGS)
        before_total = Product.objects.count()
        before_published = Product.objects.filter(status=Product.Status.PUBLISHED).count()
        remove_count = to_remove.count()

        self.stdout.write("")
        self.stdout.write(self.style.WARNING("=== BEFORE ==="))
        self.stdout.write(f"Products total:     {before_total}")
        self.stdout.write(f"Products published: {before_published}")
        self.stdout.write(f"To remove:          {remove_count}")
        self.stdout.write(f"Expected after:     {before_total - remove_count}")

        if remove_count:
            self.stdout.write("")
            self.stdout.write("Products to delete:")
            for product in to_remove.order_by("product_code"):
                self.stdout.write(f"  - {product.product_code} ({product.slug})")

        missing_slugs = CLIENT_REMOVED_PRODUCT_SLUGS - set(
            to_remove.values_list("slug", flat=True)
        )
        if missing_slugs:
            self.stdout.write("")
            self.stdout.write(
                self.style.NOTICE(
                    f"Not in DB ({len(missing_slugs)}): {', '.join(sorted(missing_slugs))}"
                )
            )

        if dry_run:
            self.stdout.write(self.style.SUCCESS("Dry run complete — no changes made."))
            return

        with transaction.atomic():
            deleted, _ = to_remove.delete()
            empty_categories = Category.objects.filter(products__isnull=True)
            deactivated = empty_categories.update(is_active=False)

        after_total = Product.objects.count()
        after_published = Product.objects.filter(status=Product.Status.PUBLISHED).count()
        after_categories = Category.objects.filter(is_active=True).count()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== AFTER ==="))
        self.stdout.write(f"Products deleted:   {deleted}")
        self.stdout.write(f"Products total:     {after_total}")
        self.stdout.write(f"Products published: {after_published}")
        self.stdout.write(f"Active categories:  {after_categories}")
        self.stdout.write(f"Empty categories deactivated: {deactivated}")
