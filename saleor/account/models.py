import logging
import os
from typing import Set
from uuid import uuid1

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Permission,
    PermissionsMixin,
)
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, FileExtensionValidator
from django.db import models
from django.db.models import Q, Value
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django_countries.fields import Country, CountryField
from oauthlib.common import generate_token
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField
from pypinyin import Style
from stdimage import StdImageField
from versatileimagefield.fields import VersatileImageField

from saleor.core.django.models import PinYinFieldModelMixin, ResizeUploadedImageModelMixin
from saleor.core.django.storage import OverwriteStorage
from saleor.site import AuthenticationBackends
from . import CustomerEvents
from .tasks import guetzli_compress_image
from .validators import validate_possible_number
from ..core.models import ModelWithMetadata
from ..core.utils.json_serializer import CustomJsonEncoder

logger = logging.getLogger(__name__)


class PossiblePhoneNumberField(PhoneNumberField):
    """Less strict field for phone numbers written to database."""

    default_validators = [validate_possible_number]


class AddressQueryset(models.QuerySet):
    def annotate_default(self, user):
        # Set default shipping/billing address pk to None
        # if default shipping/billing address doesn't exist
        default_shipping_address_pk, default_billing_address_pk = None, None
        if user.default_shipping_address:
            default_shipping_address_pk = user.default_shipping_address.pk
        if user.default_billing_address:
            default_billing_address_pk = user.default_billing_address.pk

        return user.addresses.annotate(
            user_default_shipping_address_pk=Value(
                default_shipping_address_pk, models.IntegerField()
            ),
            user_default_billing_address_pk=Value(
                default_billing_address_pk, models.IntegerField()
            ),
        )


def get_id_photo_front_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{instance.id_number or uuid1().hex}_front.{ext}'
    file_path = os.path.join(settings.ID_PHOTO_FOLDER, filename)

    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    guetzli_compress_image.apply_async(args=[full_path], countdown=10)
    return file_path


def get_id_photo_back_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{instance.id_number or uuid1().hex}_back.{ext}'
    file_path = os.path.join(settings.ID_PHOTO_FOLDER, filename)

    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    guetzli_compress_image.apply_async(args=[full_path], countdown=230)
    return file_path


class Address(PinYinFieldModelMixin, ResizeUploadedImageModelMixin, models.Model):
    first_name = models.CharField(pgettext_lazy(
        "Customer form: Given name field", "Given name"
    ), max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    company_name = models.CharField(max_length=256, blank=True)
    street_address_1 = models.CharField(pgettext_lazy(
        "Address", "Address"
    ), max_length=256, blank=True)
    street_address_2 = models.CharField(max_length=256, blank=True)
    city = models.CharField(pgettext_lazy(
        "City", "City"
    ), max_length=256, blank=True)
    city_area = models.CharField(pgettext_lazy(
        "City area", "District"
    ), max_length=128, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = CountryField(pgettext_lazy(
        "Address field", "County"
    ), blank=True)
    country_area = models.CharField(pgettext_lazy(
        "Address field", "Province"
    ), max_length=128, blank=True)
    phone = models.CharField(pgettext_lazy(
        "Phone number", "Phone number"
    ), blank=True, default="", max_length=32)
    id_number = models.CharField(_('ID number'), max_length=20, blank=True, null=True)
    id_photo_front = StdImageField(_('ID Front'), upload_to=get_id_photo_front_path, blank=True, null=True,
                                   validators=[FileExtensionValidator(['jpg', 'jpeg', 'gif', 'png'])],
                                   storage=OverwriteStorage(),
                                   variations={
                                       'thumbnail': (300, 200, False)
                                   })
    id_photo_back = StdImageField(_('ID Back'), upload_to=get_id_photo_back_path, blank=True, null=True,
                                  validators=[FileExtensionValidator(['jpg', 'jpeg', 'gif', 'png'])],
                                  storage=OverwriteStorage(),
                                  variations={
                                      'thumbnail': (300, 200, False)
                                  })
    pinyin = models.TextField(_('pinyin'), max_length=1024, blank=True)

    pinyin_fields_conf = [
        ('first_name', Style.NORMAL, False),
        ('first_name', Style.FIRST_LETTER, False),
        ('street_address_1', Style.NORMAL, False),
        ('street_address_1', Style.FIRST_LETTER, False),
    ]

    objects = AddressQueryset.as_manager()

    class Meta:
        ordering = ("pk",)

    def __init__(self, *args, **kwargs):
        super(Address, self).__init__(*args, **kwargs)
        self._state.id_number = self.id_number

    @property
    def province(self):
        return self.country_area

    @property
    def district(self):
        return self.city_area

    @property
    def full_name(self):
        return self.first_name

    @property
    def name(self):
        return self.first_name

    def __str__(self):
        return f'{self.first_name}, {self.phone}, {self.street_address_1}'

    def __eq__(self, other):
        if not isinstance(other, Address):
            return False
        return self.as_data() == other.as_data()

    __hash__ = models.Model.__hash__

    def as_data(self):
        """Return the address as a dict suitable for passing as kwargs.

        Result does not contain the primary key or an associated user.
        """
        data = model_to_dict(self, exclude=["id", "user"])
        if isinstance(data["country"], Country):
            data["country"] = data["country"].code
        if isinstance(data["phone"], PhoneNumber):
            data["phone"] = data["phone"].as_e164
        return data

    def get_copy(self):
        """Return a new instance of the same address."""
        return Address.objects.create(**self.as_data())

    def save(self, *args, **kwargs):
        # resize images when first uploaded
        self.resize_image('id_photo_front')
        self.resize_image('id_photo_back')
        if self.id_number and 'x' in self.id_number:
            self.id_number = self.id_number.upper()

        self._link_id_photo()
        super(Address, self).save(*args, **kwargs)

    def _link_id_photo(self):
        """
        reuse id photo if already uploaded
        """
        if self._state.id_number != self.id_number and self.id_number:
            if not self.id_photo_front:
                existed = Address.objects.filter(id_number=self.id_number, id_photo_front__isnull=False).first()
                if existed:
                    self.id_photo_front = existed.id_photo_front
            if not self.id_photo_back:
                existed = Address.objects.filter(id_number=self.id_number, id_photo_back__isnull=False).first()
                if existed:
                    self.id_photo_back = existed.id_photo_back


class UserManager(BaseUserManager):
    def create_user(
            self, email, password=None, is_staff=False, is_active=True, **extra_fields
    ):
        """Create a user instance with the given email and password."""
        logger.debug(f'[CREATE_USER] extra_fields={extra_fields}')
        email = UserManager.normalize_email(email)
        # Google OAuth2 backend send unnecessary username field
        extra_fields.pop("username", None)

        user = self.model(
            email=email, is_active=is_active, is_staff=is_staff, **extra_fields
        )
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(
            email, password, is_staff=True, is_superuser=True, **extra_fields
        )

    def customers(self):
        return self.get_queryset().filter(
            Q(is_staff=False) | (Q(is_staff=True) & Q(orders__isnull=False))
        )

    def staff(self):
        return self.get_queryset().filter(is_staff=True)

    def weixinmp(self):
        return self.filter(social_auth__provider=AuthenticationBackends.WEIXINMP)

    def weibo(self):
        return self.filter(social_auth__provider=AuthenticationBackends.WEIBO)

    def qq(self):
        return self.filter(social_auth__provider=AuthenticationBackends.QQ)


class User(PermissionsMixin, ModelWithMetadata, AbstractBaseUser):
    email = models.EmailField(pgettext_lazy(
        "Email", "Email"
    ), unique=True)
    first_name = models.CharField(max_length=256, blank=False)  # real name
    last_name = models.CharField(max_length=256, blank=True)  # weixin nick name
    addresses = models.ManyToManyField(
        Address, blank=True, related_name="user_addresses"
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    note = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    default_shipping_address = models.ForeignKey(
        Address, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )
    default_billing_address = models.ForeignKey(
        Address, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )
    avatar = VersatileImageField(upload_to="user-avatars", blank=True, null=True, max_length=512)
    # weixin profile
    phone = models.CharField(pgettext_lazy(
        "Phone number", "Phone number"
    ), blank=True, default="", max_length=256)
    openid = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=256, blank=True)
    province = models.CharField(max_length=256, blank=True)
    country = models.CharField(max_length=256, blank=True)
    language = models.CharField(max_length=256, blank=True)
    sex = models.CharField(verbose_name="sex", max_length=32, blank=True, null=True)

    USERNAME_FIELD = "email"

    objects = UserManager()

    class Meta:
        permissions = (
            (
                "manage_users",
                pgettext_lazy("Permission description", "Manage customers."),
            ),
            ("manage_staff", pgettext_lazy("Permission description", "Manage staff.")),
            (
                "impersonate_users",
                pgettext_lazy("Permission description", "Impersonate customers."),
            ),
        )

    pinyin_fields_conf = [
        ('first_name', Style.NORMAL, False),
        ('first_name', Style.FIRST_LETTER, False),
        ('note', Style.NORMAL, False),
        ('note', Style.FIRST_LETTER, False),
    ]

    @property
    def full_name(self):
        if self.first_name == self.last_name:
            return self.first_name
        if self.first_name and self.last_name:
            return f'{self.first_name} / {self.last_name}'
        return self.last_name or self.first_name

    @property
    def real_name(self):
        return self.first_name

    @property
    def nickname(self):
        return self.last_name

    def get_full_name(self):
        return self.full_name

    def get_ajax_label(self):
        address = self.default_billing_address
        if address:
            return "%s %s (%s)" % (address.first_name, address.last_name, self.email)
        return self.email

    @property
    def avatar_url(self):
        val = URLValidator()
        try:
            url = str(self.avatar)
            val(url)
            return url
        except ValidationError:
            return self.avatar.url if self.avatar else None

    @cached_property
    def social_user(self):
        return self.social_auth.first()

    @cached_property
    def auth_source(self):
        if self.social_user:
            return self.social_user.provider
        return None

    @cached_property
    def access_token(self):
        access_token = self.private_meta.get('access_token')
        if access_token:
            return access_token

        if self.social_user:
            if self.auth_source == AuthenticationBackends.WEIXINMP:
                return self.social_user.extra_data.get('access_token')


class ServiceAccount(ModelWithMetadata):
    name = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("service account permissions"),
        blank=True,
        help_text=_("Specific permissions for this service."),
        related_name="service_set",
        related_query_name="service",
    )

    class Meta:
        permissions = (
            (
                "manage_service_accounts",
                pgettext_lazy("Permission description", "Manage service account"),
            ),
        )

    def _get_permissions(self) -> Set[str]:
        """Return the permissions of the service."""
        if not self.is_active:
            return set()
        perm_cache_name = "_service_perm_cache"
        if not hasattr(self, perm_cache_name):
            perms = self.permissions.all()
            perms = perms.values_list("content_type__app_label", "codename").order_by()
            setattr(self, perm_cache_name, {f"{ct}.{name}" for ct, name in perms})
        return getattr(self, perm_cache_name)

    def has_perms(self, perm_list):
        """Return True if the service has each of the specified permissions."""
        if not self.is_active:
            return False

        wanted_perms = set(perm_list)
        actual_perms = self._get_permissions()

        return (wanted_perms & actual_perms) == wanted_perms

    def has_perm(self, perm):
        """Return True if the service has the specified permission."""
        if not self.is_active:
            return False

        return perm in self._get_permissions()


class ServiceAccountToken(models.Model):
    service_account = models.ForeignKey(
        ServiceAccount, on_delete=models.CASCADE, related_name="tokens"
    )
    name = models.CharField(blank=True, default="", max_length=128)
    auth_token = models.CharField(default=generate_token, unique=True, max_length=30)


class CustomerNote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    date = models.DateTimeField(db_index=True, auto_now_add=True)
    content = models.TextField()
    is_public = models.BooleanField(default=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notes", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("date",)


class CustomerEvent(models.Model):
    """Model used to store events that happened during the customer lifecycle."""

    date = models.DateTimeField(default=timezone.now, editable=False)
    type = models.CharField(
        max_length=255,
        choices=[
            (type_name.upper(), type_name) for type_name, _ in CustomerEvents.CHOICES
        ],
    )

    order = models.ForeignKey("order.Order", on_delete=models.SET_NULL, null=True)
    parameters = JSONField(blank=True, default=dict, encoder=CustomJsonEncoder)

    user = models.ForeignKey(User, related_name="events", on_delete=models.CASCADE)

    class Meta:
        ordering = ("date",)

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.type!r}, user={self.user!r})"
