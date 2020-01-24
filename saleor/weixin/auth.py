import hashlib
import logging
import os

from django.conf import settings
from social_core.pipeline.user import user_details

logger = logging.getLogger(__name__)


def CheckSign(requests):
    os.getpid()
    form = {}
    form['signature'] = requests.GET.get('signature', None)
    form['timestamp'] = requests.GET.get('timestamp', None)
    form['nonce'] = requests.GET.get('nonce', None)
    form['token'] = settings.WEIXIN_APP_TOKEN
    Signature = form.pop('signature')
    Key = hashlib.sha1("".join(sorted([form[i] for i in form])).encode('utf-8')).hexdigest()  # 获得sha1加密后结果
    return True if Signature == Key else False


def custom_user_details(strategy, details, user=None, *args, **kwargs):
    """Update user details using data from provider."""

    logger.warning('details', details)
    logger.warning('user', user)
    logger.warning('args', args)
    logger.warning('kwargs', kwargs)

    return user_details(strategy, details, user=None, *args, **kwargs),

    # if not user:
    #     return
    #
    # changed = False  # flag to track changes
    # protected = ('username', 'id', 'pk', 'email') + \
    #             tuple(strategy.setting('PROTECTED_USER_FIELDS', []))
    #
    # # Update user model attributes with the new data sent by the current
    # # provider. Update on some attributes is disabled by default, for
    # # example username and id fields. It's also possible to disable update
    # # on fields defined in SOCIAL_AUTH_PROTECTED_USER_FIELDS.
    # for name, value in details.items():
    #     if value is None or not hasattr(user, name) or name in protected:
    #         continue
    #
    #     # Check https://github.com/omab/python-social-auth/issues/671
    #     current_value = getattr(user, name, None)
    #     if current_value or current_value == value:
    #         continue
    #
    #     changed = True
    #     setattr(user, name, value)
    #
    # if changed:
    #     strategy.storage.user.changed(user)
