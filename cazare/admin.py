"""
Configurarea panoului de administrare Django.

Înregistrăm modelele noastre pentru a putea fi gestionate
din panoul de administrare Django (/admin/).
"""

from django.contrib import admin
from .models import Profil, Cladire, Camera, Rezervare, Plata

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    """Configurare pentru afișarea profilurilor în admin."""
    list_display = ['user', 'rol', 'facultate', 'an_studiu', 'telefon']
    list_filter = ['rol', 'facultate']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(Cladire)
class CladireAdmin(admin.ModelAdmin):
    """Configurare pentru afișarea clădirilor în admin."""
    list_display = ['nume', 'adresa', 'numar_etaje']

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    """Configurare pentru afișarea camerelor în admin."""
    list_display = ['numar', 'cladire', 'etaj', 'numar_locuri',
                    'locuri_disponibile', 'pret_lunar']
    list_filter = ['cladire', 'etaj']
    search_fields = ['numar']

@admin.register(Rezervare)
class RezervareAdmin(admin.ModelAdmin):
    """Configurare pentru afișarea rezervărilor în admin."""
    list_display = ['cod_unic', 'student', 'camera', 'status',
                    'data_start', 'data_sfarsit', 'data_creare']
    list_filter = ['status', 'data_start']
    search_fields = ['cod_unic', 'student__username', 'student__first_name']
    readonly_fields = ['cod_unic', 'qr_code']

@admin.register(Plata)
class PlataAdmin(admin.ModelAdmin):
    """Configurare pentru afișarea plăților în admin."""
    list_display = ['rezervare', 'suma', 'status', 'stripe_payment_id', 'data_plata']
    list_filter = ['status']
    search_fields = ['stripe_payment_id', 'rezervare__cod_unic']
