from django.contrib import admin
from django.urls import path
from MariaAlvezApp.views import painel_gerencial

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/painel-gerencial/', painel_gerencial, name='painel_gerencial'),
    path('admin/', admin.site.urls),
    path('', include('MariaAlvezApp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
