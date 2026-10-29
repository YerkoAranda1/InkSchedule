from django.contrib import admin
from django.urls import path, include
from booking.views import CustomAuthToken # <-- Esta es la clave
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('booking.urls')),
    path('api/login/', CustomAuthToken.as_view()), # <-- Sobreescribe el login por defecto
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)