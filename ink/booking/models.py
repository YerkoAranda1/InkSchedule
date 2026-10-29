from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    base_rate = models.IntegerField(help_text="Tarifa base en CLP")

    def __str__(self):
        return f"Tatuador: {self.user.username}"

class PortfolioImage(models.Model):
    artist = models.ForeignKey(Artist, related_name='portfolio', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='portfolio/')
    style = models.CharField(max_length=50, help_text="Ej. Realismo, Minimalista")
    body_part = models.CharField(max_length=50)

    class Meta:
        ordering = ['-id']  # las más nuevas primero

    def __str__(self):
        return f"{self.style} - {self.artist.user.username}"

class QuoteRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobado por Artista'),
        ('PAID', 'Abono Pagado'),
        ('REJECTED', 'Rechazado'),
    ]
    
    # NUEVO: Enlazamos la cotización a una cuenta de usuario real
    client_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    style = models.CharField(max_length=50)
    size_cm = models.IntegerField(help_text="Tamaño aproximado en cm")
    body_part = models.CharField(max_length=50)
    is_color = models.BooleanField(default=False)
    
    min_estimate = models.IntegerField(blank=True, null=True)
    max_estimate = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def calculate_estimated_range(self):
        # Lógica matemática del MVP para el presupuesto inteligente
        base = self.artist.base_rate
        size_factor = self.size_cm * 1500  # $1.500 CLP por centímetro adicional
        
        # Multiplicadores de ejemplo según zona (Idealmente esto vendría de otra tabla)
        zone_multiplier = 1.3 if self.body_part.lower() in ['costillas', 'cuello', 'manos'] else 1.0
        color_extra = 15000 if self.is_color else 0

        estimated_total = (base + size_factor + color_extra) * zone_multiplier
        
        # Generar un rango de +- 15% para dar margen al artista
        self.min_estimate = int(estimated_total * 0.85)
        self.max_estimate = int(estimated_total * 1.15)

    def save(self, *args, **kwargs):
        if not self.min_estimate or not self.max_estimate:
            self.calculate_estimated_range()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cotización de {self.client_name} para {self.artist.user.username}"