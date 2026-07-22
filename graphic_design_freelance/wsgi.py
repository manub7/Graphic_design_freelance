"""
WSGI config for graphic_design_freelance project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphic_design_freelance.settings')

application = get_wsgi_application()

# Keep the Render free-tier service from spinning down (no-op off Render).
from graphic_design_freelance.keepalive import start_keepalive  # noqa: E402
start_keepalive()
