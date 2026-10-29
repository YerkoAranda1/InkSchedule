from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArtistViewSet, QuoteRequestViewSet, ClientRegisterView, PortfolioImageViewSet

router = DefaultRouter()
router.register(r'artists', ArtistViewSet)
router.register(r'quotes', QuoteRequestViewSet, basename='quote')
router.register(r'portfolio', PortfolioImageViewSet, basename='portfolio')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', ClientRegisterView.as_view()), # <-- Nuevo endpoint
]