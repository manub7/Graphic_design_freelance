"""
Import media/ image files as a private gallery for a single user.

For each image in MEDIA_ROOT this creates a completed DesignRequest owned by
the given user's Client, plus an Order linking it to them - which is what makes
it appear under that user's "My Requests" (with a downloadable image). Because
the designs are owned (client set), they stay off the public home gallery,
which only shows unowned portfolio designs (client__isnull=True).

Usage (e.g. in the Render Shell):
    python manage.py import_gallery --email blagem1@gmail.com

Safe to re-run: images already imported for that user are skipped.
"""

import os
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from profiles.models import Client
from design_requests.models import DesignRequest, Category
from orders.models import Order

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp')


class Command(BaseCommand):
    help = "Create a private gallery of the media/ images for one user (by email)."

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True,
                            help="Email of the user who should own the gallery.")
        parser.add_argument('--category', default='Gallery',
                            help="Category name to assign (created if missing).")
        parser.add_argument('--dry-run', action='store_true',
                            help="List what would be created without writing.")

    def handle(self, *args, **options):
        User = get_user_model()
        email = options['email']

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise CommandError(f"No user found with email {email!r}.")
        except User.MultipleObjectsReturned:
            raise CommandError(f"More than one user has email {email!r}; resolve that first.")

        client, _ = Client.objects.get_or_create(user=user)

        media_root = settings.MEDIA_ROOT
        if not os.path.isdir(media_root):
            raise CommandError(f"MEDIA_ROOT does not exist: {media_root}")

        files = sorted(
            f for f in os.listdir(media_root)
            if f.lower().endswith(IMAGE_EXTENSIONS)
            and os.path.isfile(os.path.join(media_root, f))
        )
        if not files:
            self.stdout.write(self.style.WARNING(f"No image files found in {media_root}."))
            return

        dry = options['dry_run']
        if dry:
            self.stdout.write(f"[dry-run] {len(files)} image(s) would be imported for {email}:")
            for f in files:
                self.stdout.write(f"  - {f}")
            return

        category, _ = Category.objects.get_or_create(name=options['category'])

        created = skipped = 0
        for fname in files:
            # Idempotent: skip if this user already has this image.
            if DesignRequest.objects.filter(client=client, processed_image=fname).exists():
                skipped += 1
                continue

            design_request = DesignRequest.objects.create(
                client=client,
                category=category,
                name=os.path.splitext(fname)[0][:254],
                height=Decimal('1080'),
                width=Decimal('1920'),
                description=f'Imported gallery image ({fname}).',
                size=Decimal('6000'),
                price=Decimal('0'),
                processed_image=fname,
                is_processed=True,
                order_number='GALLERY',  # non-empty => not treated as an incomplete request
            )
            Order.objects.create(
                client=client,
                design_request=design_request,
                price=Decimal('0'),
                stripe_pid='',
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done for {email}: created {created}, skipped {skipped} (already imported)."
        ))
