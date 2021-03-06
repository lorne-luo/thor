import ast
import os.path
import time
import warnings

import dj_database_url
import dj_email_url
import django_cache_url
import environ
import sentry_sdk
from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django_prices.utils.formatting import get_currency_fraction
from sentry_sdk.integrations.django import DjangoIntegration
from social_core.pipeline.social_auth import associate_user


def get_list(text):
    return [item.strip() for item in text.split(",")]


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError("{} is an invalid value for {}".format(value, name)) from e
    return default_value


PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

# Load operating system environment variables and then prepare to use them
env = environ.Env()
env_file = os.path.join(PROJECT_ROOT, '.env')
if os.path.exists(env_file):
    env.read_env(env_file)

DEBUG = env.bool('DEBUG', False)

SITE_ID = 1

STARTUP_TIMESTAMP = int(time.time())

ROOT_URLCONF = "saleor.urls"

WSGI_APPLICATION = "saleor.wsgi.application"

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

ALLOWED_CLIENT_HOSTS = env.list('ALLOWED_CLIENT_HOSTS', default=['localhost', '127.0.0.1'])

INTERNAL_IPS = env.list('INTERNAL_IPS', default=['127.0.0.1'])

# Some cloud providers (Heroku) export REDIS_URL variable instead of CACHE_URL
REDIS_URL = env.str("REDIS_URL", default='redis://127.0.0.1:6379/4')
if REDIS_URL:
    CACHE_URL = env.str("CACHE_URL", REDIS_URL)
CACHES = {"default": django_cache_url.config()}

DATABASES = {
    "default": env.db('DATABASE_URL')
}

TIME_ZONE = "Australia/Melbourne"
LANGUAGE_CODE = "zh-hans"
LANGUAGES = [
    ("zh-hans", _("Simplified Chinese")),
    ("en", _("English")),
]
LOCALE_PATHS = [os.path.join(PROJECT_ROOT, "locale")]
USE_I18N = True
USE_L10N = True
USE_TZ = True

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

EMAIL_URL = env.str("EMAIL_URL", '')
SENDGRID_USERNAME = env.str("SENDGRID_USERNAME", '')
SENDGRID_PASSWORD = env.str("SENDGRID_PASSWORD", '')
if not EMAIL_URL and SENDGRID_USERNAME and SENDGRID_PASSWORD:
    EMAIL_URL = "smtp://%s:%s@smtp.sendgrid.net:587/?tls=True" % (
        SENDGRID_USERNAME,
        SENDGRID_PASSWORD,
    )
email_config = dj_email_url.parse(
    EMAIL_URL or "console://demo@example.com:console@example/"
)

EMAIL_FILE_PATH = email_config["EMAIL_FILE_PATH"]
EMAIL_HOST_USER = email_config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = email_config["EMAIL_HOST_PASSWORD"]
EMAIL_HOST = email_config["EMAIL_HOST"]
EMAIL_PORT = email_config["EMAIL_PORT"]
EMAIL_BACKEND = email_config["EMAIL_BACKEND"]
EMAIL_USE_TLS = email_config["EMAIL_USE_TLS"]
EMAIL_USE_SSL = email_config["EMAIL_USE_SSL"]

ENABLE_SSL = get_bool_from_env("ENABLE_SSL", False)

if ENABLE_SSL:
    SECURE_SSL_REDIRECT = not DEBUG

DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
ORDER_FROM_EMAIL = env.str("ORDER_FROM_EMAIL", DEFAULT_FROM_EMAIL)

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")
MEDIA_URL = env.str("MEDIA_URL", "/media/")

ID_PHOTO_FOLDER = 'id'

STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")
STATIC_URL = env.str("STATIC_URL", "/static/")
STATICFILES_DIRS = [
    ("assets", os.path.join(PROJECT_ROOT, "saleor", "static", "assets")),
    ("favicons", os.path.join(PROJECT_ROOT, "saleor", "static", "favicons")),
    ("images", os.path.join(PROJECT_ROOT, "saleor", "static", "images")),
    (
        "dashboard/images",
        os.path.join(PROJECT_ROOT, "saleor", "static", "dashboard", "images"),
    ),
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

context_processors = [
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.debug",
    "django.template.context_processors.i18n",
    "django.template.context_processors.media",
    "django.template.context_processors.static",
    "django.template.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.template.context_processors.request",
    "saleor.core.context_processors.default_currency",
    "saleor.checkout.context_processors.checkout_counter",
    "saleor.core.context_processors.search_enabled",
    "saleor.site.context_processors.site",
    "social_django.context_processors.backends",
    "social_django.context_processors.login_redirect",
]

loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

if not DEBUG:
    loaders = [("django.template.loaders.cached.Loader", loaders)]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_ROOT, "templates")],
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": context_processors,
            "loaders": loaders,
            "string_if_invalid": '<< MISSING VARIABLE "%s" >>' if DEBUG else "",
        },
    }
]

# Make this unique, and don't share it with anybody.
SECRET_KEY = env.str("SECRET_KEY",
                     default='adfasdfasdgsgqwwwwer323r42moefoin2asdf134`132f,l;/.;p231o3nr1`3n4o21')

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django_babel.middleware.LocaleMiddleware",
    "saleor.core.middleware.discounts",
    "saleor.core.middleware.google_analytics",
    "saleor.core.middleware.country",
    "saleor.core.middleware.currency",
    "saleor.core.middleware.site",
    "saleor.core.middleware.extensions",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "impersonate.middleware.ImpersonateMiddleware",
    "saleor.graphql.middleware.jwt_middleware",
    "saleor.graphql.middleware.service_account_middleware",
]

INSTALLED_APPS = [
    # External apps that need to go before django's
    "storages",
    # Django modules
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.auth",
    "django.contrib.postgres",
    "django.forms",
    # Local apps
    "saleor.extensions",
    "saleor.account",
    "saleor.discount",
    "saleor.giftcard",
    "saleor.product",
    "saleor.checkout",
    "saleor.core",
    "saleor.graphql",
    "saleor.menu",
    "saleor.order",
    "saleor.dashboard",
    "saleor.seo",
    "saleor.shipping",
    "saleor.search",
    "saleor.site",
    "saleor.data_feeds",
    "saleor.page",
    "saleor.payment",
    "saleor.webhook",
    # External apps
    "versatileimagefield",
    "django_babel",
    "bootstrap4",
    "django_measurement",
    "django_prices",
    "django_prices_openexchangerates",
    "django_prices_vatlayer",
    "graphene_django",
    "mptt",
    "webpack_loader",
    "social_django",
    "django_countries",
    "django_filters",
    "impersonate",
    "phonenumber_field",
    "captcha",
    "django_extensions"
]

ENABLE_DEBUG_TOOLBAR = get_bool_from_env("ENABLE_DEBUG_TOOLBAR", False)
if ENABLE_DEBUG_TOOLBAR:
    # Ensure the debug toolbar is actually installed before adding it
    try:
        __import__("debug_toolbar")
    except ImportError as exc:
        msg = (
            f"{exc} -- Install the missing dependencies by "
            f"running `pip install -r requirements_dev.txt`"
        )
        warnings.warn(msg)
    else:
        MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
        INSTALLED_APPS.append("debug_toolbar")

    DEBUG_TOOLBAR_PANELS = [
        # adds a request history to the debug toolbar
        "ddt_request_history.panels.request_history.RequestHistoryPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ]
    DEBUG_TOOLBAR_CONFIG = {"RESULTS_CACHE_SIZE": 100}

ENABLE_SILK = get_bool_from_env("ENABLE_SILK", False)
if ENABLE_SILK:
    MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")
    INSTALLED_APPS.append("silk")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["console"]},
    "formatters": {
        "verbose": {
            "format": (
                "%(levelname)s %(name)s %(message)s [PID:%(process)d:%(threadName)s]"
            )
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
            "propagate": True,
        },
        "django.server": {"handlers": ["console"], "level": "INFO", "propagate": True},
        "saleor": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
    },
}

AUTH_USER_MODEL = "account.User"

LOGIN_URL = "/account/login/"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 6},
    }
]

DEFAULT_COUNTRY = env.str("DEFAULT_COUNTRY", "CN")
DEFAULT_CURRENCY = env.str("DEFAULT_CURRENCY", "RMB")
DEFAULT_DECIMAL_PLACES = 2
DEFAULT_MAX_DIGITS = 12
DEFAULT_CURRENCY_CODE_LENGTH = 3

# The default max length for the display name of the
# sender email address.
# Following the recommendation of https://tools.ietf.org/html/rfc5322#section-2.1.1
DEFAULT_MAX_EMAIL_DISPLAY_NAME_LENGTH = 78

# note: having multiple currencies is not supported yet
AVAILABLE_CURRENCIES = [DEFAULT_CURRENCY]

COUNTRIES_OVERRIDE = {
    "EU": pgettext_lazy(
        "Name of political and economical union of european countries", "European Union"
    )
}

OPENEXCHANGERATES_API_KEY = env.str("OPENEXCHANGERATES_API_KEY", '')

# VAT configuration
# Enabling vat requires valid vatlayer access key.
# If you are subscribed to a paid vatlayer plan, you can enable HTTPS.
VATLAYER_ACCESS_KEY = env.str("VATLAYER_ACCESS_KEY", '')
VATLAYER_USE_HTTPS = env.bool("VATLAYER_USE_HTTPS", False)

# Avatax supports two ways of log in - username:password or account:license
AVATAX_USERNAME_OR_ACCOUNT = env.str("AVATAX_USERNAME_OR_ACCOUNT", '')
AVATAX_PASSWORD_OR_LICENSE = env.str("AVATAX_PASSWORD_OR_LICENSE", '')
AVATAX_USE_SANDBOX = env.bool("AVATAX_USE_SANDBOX", DEBUG)
AVATAX_COMPANY_NAME = env.str("AVATAX_COMPANY_NAME", "DEFAULT")
AVATAX_AUTOCOMMIT = env.bool("AVATAX_AUTOCOMMIT", False)

ACCOUNT_ACTIVATION_DAYS = 3

LOGIN_REDIRECT_URL = "home"

GOOGLE_ANALYTICS_TRACKING_ID = env.str("GOOGLE_ANALYTICS_TRACKING_ID", '')


def get_host():
    from django.contrib.sites.models import Site

    return Site.objects.get_current().domain


PAYMENT_HOST = get_host

PAYMENT_MODEL = "order.Payment"

SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

# Do not use cached session if locmem cache backend is used but fallback to use
# default django.contrib.sessions.backends.db instead
if not CACHES["default"]["BACKEND"].endswith("LocMemCache"):
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

MESSAGE_TAGS = {messages.ERROR: "danger"}

LOW_STOCK_THRESHOLD = 10
MAX_CHECKOUT_LINE_QUANTITY = int(env.str("MAX_CHECKOUT_LINE_QUANTITY", 50))

PAGINATE_BY = 16
DASHBOARD_PAGINATE_BY = 30
DASHBOARD_SEARCH_LIMIT = 5

bootstrap4 = {
    "set_placeholder": False,
    "set_required": False,
    "success_css_class": "",
    "form_renderers": {"default": "saleor.core.utils.form_renderer.FormRenderer"},
}

TEST_RUNNER = "tests.runner.PytestTestRunner"

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
ALLOWED_GRAPHQL_ORIGINS = env.str("ALLOWED_GRAPHQL_ORIGINS", "*")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Amazon S3 configuration
# AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
# AWS_LOCATION = os.environ.get("AWS_LOCATION", "")
# AWS_MEDIA_BUCKET_NAME = os.environ.get("AWS_MEDIA_BUCKET_NAME")
# AWS_MEDIA_CUSTOM_DOMAIN = os.environ.get("AWS_MEDIA_CUSTOM_DOMAIN")
# AWS_QUERYSTRING_AUTH = get_bool_from_env("AWS_QUERYSTRING_AUTH", False)
# AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_STATIC_CUSTOM_DOMAIN")
# AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL", None)
# AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
# AWS_DEFAULT_ACL = os.environ.get("AWS_DEFAULT_ACL", None)

# Google Cloud Storage configuration
GS_PROJECT_ID = os.environ.get("GS_PROJECT_ID")
GS_STORAGE_BUCKET_NAME = os.environ.get("GS_STORAGE_BUCKET_NAME")
GS_MEDIA_BUCKET_NAME = os.environ.get("GS_MEDIA_BUCKET_NAME")
GS_AUTO_CREATE_BUCKET = get_bool_from_env("GS_AUTO_CREATE_BUCKET", False)

# If GOOGLE_APPLICATION_CREDENTIALS is set there is no need to load OAuth token
# See https://django-storages.readthedocs.io/en/latest/backends/gcloud.html
# if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
#     GS_CREDENTIALS = os.environ.get("GS_CREDENTIALS")
#
# if AWS_STORAGE_BUCKET_NAME:
#     STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
# elif GS_STORAGE_BUCKET_NAME:
#     STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
#
# if AWS_MEDIA_BUCKET_NAME:
#     DEFAULT_FILE_STORAGE = "saleor.core.storages.S3MediaStorage"
#     THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE
# elif GS_MEDIA_BUCKET_NAME:
#     DEFAULT_FILE_STORAGE = "saleor.core.storages.GCSMediaStorage"
#     THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    "products": [
        ("product_gallery", "thumbnail__540x540"),
        ("product_gallery_2x", "thumbnail__1080x1080"),
        ("product_small", "thumbnail__60x60"),
        ("product_small_2x", "thumbnail__120x120"),
        ("product_list", "thumbnail__255x255"),
        ("product_list_2x", "thumbnail__510x510"),
    ],
    "background_images": [("header_image", "thumbnail__1080x440")],
    "user_avatars": [("default", "thumbnail__445x445")],
}

VERSATILEIMAGEFIELD_SETTINGS = {
    # Images should be pre-generated on Production environment
    "create_images_on_demand": get_bool_from_env("CREATE_IMAGES_ON_DEMAND", DEBUG)
}

PLACEHOLDER_IMAGES = {
    60: "images/placeholder60x60.png",
    120: "images/placeholder120x120.png",
    255: "images/placeholder255x255.png",
    540: "images/placeholder540x540.png",
    1080: "images/placeholder1080x1080.png",
}

DEFAULT_PLACEHOLDER = "images/placeholder255x255.png"

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "assets/",
        "STATS_FILE": os.path.join(PROJECT_ROOT, "webpack-bundle.json"),
        "POLL_INTERVAL": 0.1,
        "IGNORE": [r".+\.hot-update\.js", r".+\.map"],
    }
}

LOGOUT_ON_PASSWORD_CHANGE = False

# SEARCH CONFIGURATION
DB_SEARCH_ENABLED = True

# support deployment-dependant elastic environment variable
ES_URL = (
        os.environ.get("ELASTICSEARCH_URL")
        or os.environ.get("SEARCHBOX_URL")
        or os.environ.get("BONSAI_URL")
)

ENABLE_SEARCH = bool(ES_URL) or DB_SEARCH_ENABLED  # global search disabling

SEARCH_BACKEND = "saleor.search.backends.postgresql"

if ES_URL:
    SEARCH_BACKEND = "saleor.search.backends.elasticsearch"
    INSTALLED_APPS.append("django_elasticsearch_dsl")
    ELASTICSEARCH_DSL = {"default": {"hosts": ES_URL}}

AUTHENTICATION_BACKENDS = [
    # "saleor.account.backends.facebook.CustomFacebookOAuth2",
    # "saleor.account.backends.google.CustomGoogleOAuth2",
    "saleor.account.backends.weixin.CustomWeixinMpOAuth2",
    # "saleor.account.backends.weixin.CustomWeixinOAuth2",
    "saleor.account.backends.weibo.CustomWeiboOAuth2",
    "saleor.account.backends.qq.CustomQQOAuth2",
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

SOCIAL_AUTH_PIPELINE = [
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    # "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    # "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    # "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
]

SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"fields": "id, email"}
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
# As per March 2018, Facebook requires all traffic to go through HTTPS only
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

# CELERY SETTINGS
CELERY_BROKER_URL = (
    env.str("CELERY_BROKER_URL", '')
)
CELERY_TASK_ALWAYS_EAGER = not CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", None)

# Impersonate module settings
IMPERSONATE = {
    "URI_EXCLUSIONS": [r"^dashboard/"],
    "CUSTOM_USER_QUERYSET": "saleor.account.impersonate.get_impersonatable_users",  # noqa
    "USE_HTTP_REFERER": True,
    "CUSTOM_ALLOW": "saleor.account.impersonate.can_impersonate",
}

# Rich-text editor
ALLOWED_TAGS = [
    "a",
    "b",
    "blockquote",
    "br",
    "em",
    "h2",
    "h3",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "strong",
    "ul",
]
ALLOWED_ATTRIBUTES = {"*": ["align", "style"], "a": ["href", "title"], "img": ["src"]}
ALLOWED_STYLES = ["text-align"]

# Slugs for menus precreated in Django migrations
DEFAULT_MENUS = {"top_menu_name": "navbar", "bottom_menu_name": "footer"}

# This enable the new 'No Captcha reCaptcha' version (the simple checkbox)
# instead of the old (deprecated) one. For more information see:
#   https://github.com/praekelt/django-recaptcha/blob/34af16ba1e/README.rst
NOCAPTCHA = True

# Set Google's reCaptcha keys
RECAPTCHA_PUBLIC_KEY = env.str("RECAPTCHA_PUBLIC_KEY", '')
RECAPTCHA_PRIVATE_KEY = env.str("RECAPTCHA_PRIVATE_KEY", '')

#  Sentry
SENTRY_DSN = env.str("SENTRY_DSN", '')
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()])

GRAPHENE = {
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": True,
    "RELAY_CONNECTION_MAX_LIMIT": 100,
}

EXTENSIONS_MANAGER = "saleor.extensions.manager.ExtensionsManager"

PLUGINS = [
    "saleor.extensions.plugins.avatax.plugin.AvataxPlugin",
    "saleor.extensions.plugins.vatlayer.plugin.VatlayerPlugin",
    "saleor.extensions.plugins.webhook.plugin.WebhookPlugin",
    "saleor.payment.gateways.dummy.plugin.DummyGatewayPlugin",
    "saleor.payment.gateways.stripe.plugin.StripeGatewayPlugin",
    "saleor.payment.gateways.braintree.plugin.BraintreeGatewayPlugin",
    "saleor.payment.gateways.razorpay.plugin.RazorpayGatewayPlugin",
]

# Whether DraftJS should be used be used instead of HTML
# True to use DraftJS (JSON based), for the 2.0 dashboard
# False to use the old editor from dashboard 1.0
USE_JSON_CONTENT = env.bool("USE_JSON_CONTENT", False)

WEIXIN_APP_ID = env.str('SOCIAL_AUTH_WEIXIN_KEY')
WEIXIN_APP_SECRET = env.str('SOCIAL_AUTH_WEIXIN_SECRET')
WEIXIN_APP_TOKEN = env.str('WEIXIN_APP_TOKEN')
