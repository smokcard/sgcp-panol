from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from authentication.views import root_redirect_view

urlpatterns = [
    path('', root_redirect_view, name='root'),
    path('auth/', include('authentication.urls')),
    path('inventario/', include('inventario.urls')),
    path('prestamos/', include('prestamos.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
