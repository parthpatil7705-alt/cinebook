"""
Production settings for CineBook.
Uses PostgreSQL, Redis cache, and secure configurations.
"""
from .base import *  # noqa: F401, F403
import environ

env = environ.Env()

DEBUG = False

# Database — PostgreSQL
DATABASES = {
    'default': env.db('DATABASE_URL'),
}

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Redis cache in production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
    }
}

# Use real SMTP email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
