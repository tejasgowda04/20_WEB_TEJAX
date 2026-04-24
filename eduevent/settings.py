"""
EduEvent – Django Settings
Unified College Event & Venue Management System (P-04)
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-eduevent-dev-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')]

# ── Applications ─────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    # Local
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eduevent.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR, BASE_DIR / 'pages'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.firebase_config',
                'core.context_processors.college_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'eduevent.wsgi.application'

# ── Database (Supabase PostgreSQL / Render) ─────────────────────────
# Use dj-database-url to parse DATABASE_URL from environment
# Supports both Render (DATABASE_URL) and Supabase (individual DB_* vars)
database_url = os.getenv('DATABASE_URL', '')
if database_url:
    # Parse Render's DATABASE_URL format
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True
        )
    }
    # Ensure SSL connection for production
    if 'OPTIONS' not in DATABASES['default']:
        DATABASES['default']['OPTIONS'] = {}
    DATABASES['default']['OPTIONS']['sslmode'] = 'require'
elif os.getenv('DB_NAME'):
    # Fallback to individual Supabase environment variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'postgres'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '6543'),
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
else:
    # Fallback to SQLite for development without database connection
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Auth ─────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validators.MinimumLengthValidator'},
]

# ── Internationalization ─────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ── Static Files ─────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    ('css', BASE_DIR / 'css'),
    ('js', BASE_DIR / 'js'),
    ('images', BASE_DIR / 'images'),
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
if DEBUG:
    STORAGES = {
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── REST Framework ───────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.firebase_auth.FirebaseAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ── CORS ─────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# ── Email (SMTP) ────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'EduEvent <noreply@eduevent.com>')

# If no SMTP configured, use console backend for dev
if not EMAIL_HOST_USER:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ── Firebase ─────────────────────────────────────────────────────
FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', '')
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', '')
FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN', '')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', '')
FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID', '')
FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID', '')

# ── App Config ───────────────────────────────────────────────────
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')
COLLEGE_NAME = os.getenv('COLLEGE_NAME', 'EduEvent College')

# ── Login URLs ───────────────────────────────────────────────────
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
