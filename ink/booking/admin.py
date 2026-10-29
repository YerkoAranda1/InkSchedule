from django.contrib import admin
from .models import Artist, PortfolioImage, QuoteRequest

# Configuramos una vista avanzada para las cotizaciones
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'artist', 'status', 'min_estimate', 'max_estimate')
    list_filter = ('status', 'artist')
    readonly_fields = ('min_estimate', 'max_estimate') # Evita que el admin edite el cálculo manual

# Registramos los modelos simples
admin.site.register(Artist)
admin.site.register(PortfolioImage)
# Registramos la cotización con su vista personalizada
admin.site.register(QuoteRequest, QuoteRequestAdmin)