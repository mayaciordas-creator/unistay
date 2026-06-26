"""
Setările Django pentru proiectul 'camin'.

Acest fișier conține toate configurările aplicației:
- baza de date (SQLite)
- aplicațiile instalate
- template-uri și fișiere statice
- setări de autentificare
- configurare Stripe (simulare)
"""

import os
from pathlib import Path

# Directorul de bază al proiectului
BASE_DIR = Path(__file__).resolve().parent.parent

# Cheie secretă pentru dezvoltare (NU folosi în producție!)
SECRET_KEY = 'django-insecure-wz!u#82#cm1rt=5w4cpm=9q3ilkbsn*@k21)81*58u*t24y8+-'

# Modul debug activat pentru dezvoltare
DEBUG = True

ALLOWED_HOSTS = ['*']

# ============================================================
# Aplicațiile instalate
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',        # Panoul de administrare Django
    'django.contrib.auth',         # Sistem de autentificare
    'django.contrib.contenttypes', # Framework pentru tipuri de conținut
    'django.contrib.sessions',     # Managementul sesiunilor
    'django.contrib.messages',     # Sistemul de mesaje
    'django.contrib.staticfiles',  # Servirea fișierelor statice
    'django_extensions',           # Generare diagrame și utilitare
    'cazare',                      # Aplicația noastră principală
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'camin.urls'

# ============================================================
# Configurare template-uri
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Directoarele unde Django caută template-uri
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'camin.wsgi.application'

# ============================================================
# Baza de date - SQLite (default Django, simplu pentru dezvoltare)
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================================
# Validare parole
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 14}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'cazare.validators.SpecialCharacterValidator'},
    {'NAME': 'cazare.validators.UppercaseValidator'},
    {'NAME': 'cazare.validators.NumberValidator'},
]

# ============================================================
# Internaționalizare
# ============================================================
LANGUAGE_CODE = 'ro'       # Limba română
TIME_ZONE = 'Europe/Bucharest'
USE_I18N = True
USE_TZ = True

# ============================================================
# Fișiere statice (CSS, JavaScript, imagini)
# ============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ============================================================
# Fișiere media (încărcate de utilizatori, ex: coduri QR)
# ============================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================
# Setări de autentificare
# ============================================================
LOGIN_URL = '/login/'               # URL-ul paginii de autentificare
LOGIN_REDIRECT_URL = '/dashboard/'  # Redirecționare după login
LOGOUT_REDIRECT_URL = '/'           # Redirecționare după logout

# ============================================================
# Configurare Stripe (simulare / test mode)
# Înlocuiește cu cheile tale reale Stripe pentru producție
# ============================================================
STRIPE_PUBLIC_KEY = 'pk_test_simulare_cheie_publica'
STRIPE_SECRET_KEY = 'sk_test_simulare_cheie_secreta'

# Tipul câmpului de cheie primară
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# Configurare E-mail (SMTP Gmail)
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'unistay.co26@gmail.com'
EMAIL_HOST_PASSWORD = 'elasvgvbovnljgeu'
DEFAULT_FROM_EMAIL = 'UniStay <unistay.co26@gmail.com>'

SITE_URL = 'http://127.0.0.1:8000'
