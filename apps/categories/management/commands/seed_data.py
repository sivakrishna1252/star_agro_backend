from django.core.management.base import BaseCommand

from apps.categories.models import Category
from apps.products.models import (
    Product,
    ProductApplication,
    ProductBenefit,
    ProductProperty,
)
from apps.site_settings.models import SiteSettings


class Command(BaseCommand):
    help = "Load initial categories, products, and site settings for Star Agsurf Industries."

    def handle(self, *args, **options):
        SiteSettings.objects.update_or_create(
            pk=1,
            defaults={
                "site_name": "Star Agsurf Industries",
                "tagline": "Specialty Surfactants & Agrochemical Formulations",
                "about_us": (
                    "Star Agsurf Industries is a specialty chemical manufacturer "
                    "focused on surfactants and agrochemical formulations for crop "
                    "protection and textile processing."
                ),
                "vision": "To be a globally recognized leader in specialty surfactant chemistry.",
                "mission": (
                    "Deliver innovative, sustainable chemical solutions that enhance "
                    "crop protection performance and textile processing efficiency."
                ),
                "manufacturing_expertise": (
                    "Expertise in SC, EC, ME, and EW formulation systems with "
                    "client-centric custom formulation capabilities."
                ),
                "rd_focus": "Continuous innovation in wetting, dispersing, and adjuvant technologies.",
                "sustainability": "Committed to sustainable chemistry and environmentally responsible manufacturing.",
                "client_commitment": "Partnering with distributors and manufacturers worldwide.",
                "contact_email": "info@staragsurf.com",
                "contact_phone": "+91-XXXXXXXXXX",
            },
        )

        categories_data = [
            ("Crop Protection", "crop-protection", "Crop protection chemical solutions."),
            ("SC Formulations", "sc-formulations", "Suspension concentrate formulation surfactants."),
            ("EC Formulations", "ec-formulations", "Emulsifiable concentrate emulsifiers."),
            ("ME Formulations", "me-formulations", "Micro-emulsion formulation systems."),
            ("EW Formulations", "ew-formulations", "Oil-in-water emulsion systems."),
            ("Adjuvants", "adjuvants", "Proprietary adjuvants and performance enhancers."),
            ("Wetting Agents", "wetting-agents", "Specialty wetting agents."),
            ("Dispersing Agents", "dispersing-agents", "Specialty dispersing agents."),
            ("Textile Chemicals", "textile-chemicals", "Textile processing chemical range."),
        ]

        category_map = {}
        for i, (name, slug, desc) in enumerate(categories_data):
            cat, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": desc, "display_order": i, "is_active": True},
            )
            category_map[slug] = cat

        products_data = [
            ("STAGSURF D33", "stagsurf-d33", "sc-formulations", "SC", "STAGSURF D33"),
            ("STAGSURF TFL", "stagsurf-tfl", "sc-formulations", "SC", "STAGSURF TFL"),
            ("STAGSURF TFLK", "stagsurf-tflk", "sc-formulations", "SC", "STAGSURF TFLK"),
            ("STAGSURF 483", "stagsurf-483", "sc-formulations", "SC", "STAGSURF 483"),
            ("STAGSURF TSU", "stagsurf-tsu", "sc-formulations", "SC", "STAGSURF TSU"),
            ("STAGSURF SC 6875", "stagsurf-sc-6875", "sc-formulations", "SC", "STAGSURF SC 6875"),
            ("STAGSURF BS 7800", "stagsurf-bs-7800", "sc-formulations", "SC", "STAGSURF BS 7800"),
            ("STAGSURF DS 90 M", "stagsurf-ds-90-m", "ec-formulations", "EC", "STAGSURF DS 90 M"),
            ("STAGSURF WT 100", "stagsurf-wt-100", "ec-formulations", "EC", "STAGSURF WT 100"),
            ("STAGSURF PO 1000", "stagsurf-po-1000", "ec-formulations", "EC", "STAGSURF PO 1000"),
            ("STAGSURF EC 400", "stagsurf-ec-400", "ec-formulations", "EC", "STAGSURF EC 400"),
            ("STAGSURF EC 3418", "stagsurf-ec-3418", "ec-formulations", "EC", "STAGSURF EC 3418"),
            ("STAGPENT 1000 UT", "stagpent-1000-ut", "adjuvants", "ADJUVANT", "STAGPENT 1000 UT"),
            ("STAGPENT TMBO", "stagpent-tmbo", "adjuvants", "ADJUVANT", "STAGPENT TMBO"),
            ("STAGWET SW60", "stagwet-sw60", "wetting-agents", "WETTING", "STAGWET SW60"),
            ("STAGWET DW 7500", "stagwet-dw-7500", "wetting-agents", "WETTING", "STAGWET DW 7500"),
            ("STAGWET SDS", "stagwet-sds", "dispersing-agents", "DISPERSING", "STAGWET SDS"),
            ("STAGWET SLS", "stagwet-sls", "wetting-agents", "WETTING", "STAGWET SLS"),
        ]

        for i, (name, slug, cat_slug, form_type, code) in enumerate(products_data):
            product, _ = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "product_code": code,
                    "category": category_map[cat_slug],
                    "formulation_type": form_type,
                    "short_description": f"{name} — specialty surfactant for agrochemical formulations.",
                    "is_featured": i < 4,
                    "display_order": i,
                    "status": Product.Status.PUBLISHED,
                },
            )

            if slug == "stagsurf-sc-6875":
                sample_properties = [
                    ("Appearance", "Pale Yellow Liquid"),
                    ("pH", "5-7"),
                    ("Solid Content", "95%"),
                    ("Solubility", "Water Soluble"),
                ]
                for j, (prop_name, prop_value) in enumerate(sample_properties):
                    ProductProperty.objects.update_or_create(
                        product=product,
                        property_name=prop_name,
                        defaults={"property_value": prop_value, "display_order": j},
                    )

                sample_benefits = [
                    "Increases herbicide penetration",
                    "Improves retention on leaf surface",
                    "Reduces evaporation of spray droplets",
                ]
                for j, benefit in enumerate(sample_benefits):
                    ProductBenefit.objects.update_or_create(
                        product=product,
                        benefit=benefit,
                        defaults={"display_order": j},
                    )

                sample_applications = [
                    "Crop Protection",
                    "Agrochemical Formulations",
                    "SC Formulation Systems",
                ]
                for j, app_text in enumerate(sample_applications):
                    ProductApplication.objects.update_or_create(
                        product=product,
                        application_text=app_text,
                        defaults={"display_order": j},
                    )

        self.stdout.write(self.style.SUCCESS("Initial data loaded successfully."))
