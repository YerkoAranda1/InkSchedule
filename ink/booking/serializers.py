from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Artist, PortfolioImage, QuoteRequest

class ClientRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Token.objects.create(user=user)
        return user

MAX_IMAGE_MB = 5
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

class PortfolioImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioImage
        fields = ['id', 'image', 'style', 'body_part']

    def validate_image(self, image):
        if image.size > MAX_IMAGE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"La imagen no puede pesar más de {MAX_IMAGE_MB} MB.")
        if getattr(image, 'content_type', None) not in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError("Formato no permitido. Usa JPG, PNG o WebP.")
        return image

class ArtistSerializer(serializers.ModelSerializer):
    portfolio = PortfolioImageSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Artist
        fields = ['id', 'username', 'bio', 'base_rate', 'portfolio']

class QuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRequest
        fields = '__all__'
        # Añadidos client_name y client_email a los campos protegidos
        read_only_fields = ['min_estimate', 'max_estimate', 'client_name', 'client_email']