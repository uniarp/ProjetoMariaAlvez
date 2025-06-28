import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-r#c!dg_76p=4-fa90mwfh1c#ib0lyu@*$4w*vi+$pk!%k)u_pp')

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'MariaAlvezApp',
    'Terceiros', 
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

ROOT_URLCONF = 'MariaAlvez.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'MariaAlvez.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT'),
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

JAZZMIN_SETTINGS = {
    "site_logo": "img/logo.png",
    "site_logo_classes": "img-circle elevation-3",
    "site_logo_icon": None,
    "site_title": "Centro de Bem Estar Animal - Maria Alvez",
    "site_header": "Centro de Bem Estar Animal - Maria Alvez",
    "site_brand": "CBEA Maria Alves",
    "welcome_sign": "Centro de Bem Estar Animal Maria Alvez",
    "copyright": "CBEA Maria Alves",
    "custom_css": "css/custom_admin.css",
    "topmenu_links": [
        {"name": "Início", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "MariaAlvezApp.Tutor"},
        {"model": "MariaAlvezApp.Animal"},
    ],

    "icons": {
        "auth.Group": "fas fa-users",
        "auth.User": "fas fa-user",
        "MariaAlvezApp.Veterinario": "fas fa-user-md",
        "MariaAlvezApp.Tutor": "fas fa-user",
        "MariaAlvezApp.Animal": "fas fa-paw",
        "MariaAlvezApp.ConsultaClinica": "fas fa-stethoscope",
        "MariaAlvezApp.AgendamentoConsultas": "fas fa-calendar-check",
        "MariaAlvezApp.EstoqueMedicamento": "fas fa-capsules",
        "MariaAlvezApp.MovimentoEstoqueMedicamento": "fas fa-exchange-alt",
        "MariaAlvezApp.RegistroVacinacao": "fas fa-syringe",
        "MariaAlvezApp.RegistroVermifugos": "fas fa-pills",
        "MariaAlvezApp.Exames": "fas fa-vial",
        "MariaAlvezApp.RelatoriosGerais": "fas fa-file",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": True,
    "footer_small_text": True,
    "body_small_text": True,
    "brand_small_text": True,
    "accent": "accent-info",
    "navbar": "navbar-dark bg-primary",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": None,
    "custom_css": """
        .sidebar .nav-item .nav-link {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 12px;
            padding: 5px 10px;
        }
        .sidebar .nav-treeview .nav-item .nav-link {
            padding-left: 20px;
            font-size: 12px;
        }
    """,
    "custom_theme": {
        "--primary": "#006699",
        "--accent": "#4CAF50",
        "--success": "#4CAF50",
        "--info": "#006699",
        "--warning": "#FFA726",
        "--danger": "#D64541",
        "--light": "#ffffff",
        "--dark": "#2f2f2f",
        "--body-bg": "#f4f6f9",
        "--text-color": "#212529",
    },
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

