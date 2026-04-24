"""EduEvent URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve root-level css/, js/, images/ at their relative paths
    # so existing HTML files with `css/main.css`, `js/db.js`, etc. keep working
    from django.views.static import serve
    import os
    BASE_DIR = settings.BASE_DIR
    urlpatterns += [
        path('css/<path:path>', serve, {'document_root': os.path.join(BASE_DIR, 'css')}),
        path('js/<path:path>', serve, {'document_root': os.path.join(BASE_DIR, 'js')}),
        path('images/<path:path>', serve, {'document_root': os.path.join(BASE_DIR, 'images')}),
    ]
