"""graphic_design_freelance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve as media_serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('home.urls')),
    path('orders/', include('orders.urls')),
    path('design_requests/', include('design_requests.urls')),
    path('profile/', include('profiles.urls')),
]

# Serve uploaded/portfolio media. Django's static() helper only works when
# DEBUG=True, which is why images were 404ing (blank gallery) in production.
# Serve them explicitly unless media is offloaded to S3/Supabase (USE_AWS),
# in which case MEDIA_URL is an absolute https URL and needs no local route.
if not settings.MEDIA_URL.startswith('http'):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', media_serve,
                {'document_root': settings.MEDIA_ROOT}),
    ]
