from rest_framework import viewsets, permissions, generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import Artist, PortfolioImage, QuoteRequest
from .serializers import (
    ArtistSerializer,
    PortfolioImageSerializer,
    QuoteRequestSerializer,
    ClientRegistrationSerializer,
)

# NUEVO: Login Inteligente que detecta el rol
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        token, created = Token.objects.get_or_create(user=user)
        is_artist = Artist.objects.filter(user=user).exists()
        
        return Response({
            'token': token.key,
            'is_artist': is_artist,
            'username': user.username
        })

class ClientRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ClientRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [permissions.AllowAny] 

class QuoteRequestViewSet(viewsets.ModelViewSet):
    serializer_class = QuoteRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Sin PUT ni DELETE: solo crear, leer y cambiar estado
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def _is_artist(self):
        return Artist.objects.filter(user=self.request.user).exists()

    def get_queryset(self):
        user = self.request.user
        if self._is_artist():
            return QuoteRequest.objects.filter(artist__user=user)
        return QuoteRequest.objects.filter(client_user=user)

    def perform_create(self, serializer):
        if self._is_artist():
            raise PermissionDenied("Los tatuadores no pueden crear cotizaciones.")
        user = self.request.user
        serializer.save(
            status='PENDING',
            client_user=user,
            client_name=user.username,
            client_email=user.email
        )

    def partial_update(self, request, *args, **kwargs):
        if not self._is_artist():
            raise PermissionDenied("Solo el tatuador puede modificar una cotización.")

        if set(request.data.keys()) - {'status'}:
            raise ValidationError("Solo se puede modificar el campo 'status'.")

        if request.data.get('status') not in ('PENDING', 'APPROVED', 'REJECTED'):
            raise ValidationError("Estado no permitido.")

        if self.get_object().status == 'PAID':
            raise ValidationError("Una cotización con abono pagado no se puede modificar.")

        return super().partial_update(request, *args, **kwargs)

MAX_PORTFOLIO_IMAGES = 30

class PortfolioImageViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        # Cada tatuador solo ve y borra sus propias fotos
        return PortfolioImage.objects.filter(artist__user=self.request.user)

    def perform_create(self, serializer):
        try:
            artist = Artist.objects.get(user=self.request.user)
        except Artist.DoesNotExist:
            raise PermissionDenied("Solo los tatuadores pueden subir fotos.")
        if artist.portfolio.count() >= MAX_PORTFOLIO_IMAGES:
            raise ValidationError(f"Máximo {MAX_PORTFOLIO_IMAGES} fotos por portafolio.")
        serializer.save(artist=artist)

    def perform_destroy(self, instance):
        instance.image.delete(save=False)  # borra también el archivo del disco
        instance.delete()