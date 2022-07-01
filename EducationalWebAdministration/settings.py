from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = False

ALLOWED_HOSTS = ["localhost", "educationalweb", "192.168.1.94"]  # последний ip - для локальной сети (ставь свой)
CSRF_TRUSTED_ORIGINS = ["http://localhost:49145", "http://192.168.1.94:49145"] # последний ip - для локальной сети (ставь свой)

INSTALLED_APPS = [
    'EducationalWeb',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'EducationalWeb/templates'],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': env('USER'),
        'PASSWORD': env('PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'NAME': env('NAME'),
        'PORT': env('POSTGRES_PORT'),
        'CONN_MAX_AGE': int(env('CONNECTION_TIMEOUT')),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'mihalis': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'systemd': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        }
    },
}

CACHES = {
    'default': {
        # To make faking cache: django.core.cache.backends.dummy.DummyCache
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env("REDIS_HOST"),
        'TIMEOUT': int(env("REDIS_TIMEOUT")),
        'KEY_PREFIX': env("CACHE_PREFIX"),
        'OPTIONS': {
            'db': int(env("REDIS_DB")),
            # 'PARSER_CLASS': 'redis.connection.HiredisParser',
        },
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [env("REDIS_HOST")]
        },
    }
}

WSGI_APPLICATION = 'EducationalWebAdministration.wsgi.application'
ASGI_APPLICATION = 'EducationalWebAdministration.asgi.application'

ROOT_URLCONF = 'EducationalWebAdministration.urls'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

# where collectstatic will place all files
STATIC_ROOT = BASE_DIR / 'EducationalWeb/static'

# where will the static files come from
# STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# установлено None, т.к. сайт сейчас не поддерживает https, поэтому браузер выдает ошибку 'The Cross-Origin-Opener-Policy header has been ignored'
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = int(env("REDIS_TIMEOUT"))
CACHE_MIDDLEWARE_KEY_PREFIX = env("CACHE_PAGE_PREFIX")
CSRF_COOKIE_SECURE = False
