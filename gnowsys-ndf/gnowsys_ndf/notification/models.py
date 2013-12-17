import cPickle as pickle

from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language, activate

from django.contrib.auth.models import User

from notification import backends


DEFAULT_QUEUE_ALL = False
QUEUE_ALL = getattr(settings, "NOTIFICATION_QUEUE_ALL", DEFAULT_QUEUE_ALL)
NOTIFICATION_BACKENDS = backends.load_backends()
NOTICE_MEDIA, NOTICE_MEDIA_DEFAULTS = backends.load_media_defaults(
    backends=NOTIFICATION_BACKENDS
)


class LanguageStoreNotAvailable(Exception):
    pass


def create_notice_type(label, display, description, **kwargs):
    NoticeType.create(label, display, description, **kwargs)


class NoticeType(models.Model):
    
    label = models.CharField(_("label"), max_length=40)
    display = models.CharField(_("display"), max_length=50)
    description = models.CharField(_("description"), max_length=100)
    
    # by default only on for media with sensitivity less than or equal to this number
    default = models.IntegerField(_("default"))
    
    def __unicode__(self):
        return self.label
    
    class Meta:
        verbose_name = _("notice type")
        verbose_name_plural = _("notice types")
    
    @classmethod
    def create(cls, label, display, description, default=2, verbosity=1):
        """
        Creates a new NoticeType.
        
        This is intended to be used by other apps as a post_syncdb manangement step.
        """
        try:
            notice_type = cls._default_manager.get(label=label)
            updated = False
            if display != notice_type.display:
                notice_type.display = display
                updated = True
            if description != notice_type.description:
                notice_type.description = description
                updated = True
            if default != notice_type.default:
                notice_type.default = default
                updated = True
            if updated:
                notice_type.save()
                if verbosity > 1:
                    print "Updated %s NoticeType" % label
        except cls.DoesNotExist:
            cls(label=label, display=display, description=description, default=default).save()
            if verbosity > 1:
                print "Created %s NoticeType" % label


class NoticeSetting(models.Model):
    """
    Indicates, for a given user, whether to send notifications
    of a given type to a given medium.
    """
    
    user = models.ForeignKey(User, verbose_name=_("user"))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_("notice type"))
    medium = models.CharField(_("medium"), max_length=1, choices=NOTICE_MEDIA)
    send = models.BooleanField(_("send"))
    
    class Meta:
        verbose_name = _("notice setting")
        verbose_name_plural = _("notice settings")
        unique_together = ("user", "notice_type", "medium")
    
    @classmethod
    def for_user(cls, user, notice_type, medium):
        try:
            return cls._default_manager.get(user=user, notice_type=notice_type, medium=medium)
        except cls.DoesNotExist:
            default = (NOTICE_MEDIA_DEFAULTS[medium] <= notice_type.default)
            setting = cls(user=user, notice_type=notice_type, medium=medium, send=default)
            setting.save()
            return setting


class NoticeQueueBatch(models.Model):
    """
    A queued notice.
    Denormalized data for a notice.
    """
    pickled_data = models.TextField()


def get_notification_language(user):
    """
    Returns site-specific notification language for this user. Raises
    LanguageStoreNotAvailable if this site does not use translated
    notifications.
    """
    if getattr(settings, "NOTIFICATION_LANGUAGE_MODULE", False):
        try:
            app_label, model_name = settings.NOTIFICATION_LANGUAGE_MODULE.split(".")
            model = models.get_model(app_label, model_name)
            # pylint: disable-msg=W0212
            language_model = model._default_manager.get(user__id__exact=user.id)
            if hasattr(language_model, "language"):
                return language_model.language
        except (ImportError, ImproperlyConfigured, model.DoesNotExist):
            raise LanguageStoreNotAvailable
    raise LanguageStoreNotAvailable


def send_now(users, label, extra_context=None, sender=None):
    """
    Creates a new notice.
    
    This is intended to be how other apps create new notices.
    
    notification.send(user, "friends_invite_sent", {
        "spam": "eggs",
        "foo": "bar",
    )
    """
    sent = False
    if extra_context is None:
        extra_context = {}
    
    notice_type = NoticeType.objects.get(label=label)
    
    current_language = get_language()
    
    for user in users:
        # get user language for user from language store defined in
        # NOTIFICATION_LANGUAGE_MODULE setting
        try:
            language = get_notification_language(user)
        except LanguageStoreNotAvailable:
            language = None
        
        if language is not None:
            # activate the user's language
            activate(language)
        
        for backend in NOTIFICATION_BACKENDS.values():
            if backend.can_send(user, notice_type):
                backend.deliver(user, sender, notice_type, extra_context)
                sent = True
    
    # reset environment to original language
    activate(current_language)
    return sent


def send(*args, **kwargs):
    """
    A basic interface around both queue and send_now. This honors a global
    flag NOTIFICATION_QUEUE_ALL that helps determine whether all calls should
    be queued or not. A per call ``queue`` or ``now`` keyword argument can be
    used to always override the default global behavior.
    """
    queue_flag = kwargs.pop("queue", False)
    now_flag = kwargs.pop("now", False)
    assert not (queue_flag and now_flag), "'queue' and 'now' cannot both be True."
    if queue_flag:
        return queue(*args, **kwargs)
    elif now_flag:
        return send_now(*args, **kwargs)
    else:
        if QUEUE_ALL:
            return queue(*args, **kwargs)
        else:
            return send_now(*args, **kwargs)


def queue(users, label, extra_context=None, sender=None):
    """
    Queue the notification in NoticeQueueBatch. This allows for large amounts
    of user notifications to be deferred to a seperate process running outside
    the webserver.
    """
    if extra_context is None:
        extra_context = {}
    if isinstance(users, QuerySet):
        users = [row["pk"] for row in users.values("pk")]
    else:
        users = [user.pk for user in users]
    notices = []
    for user in users:
        notices.append((user, label, extra_context, sender))
    NoticeQueueBatch(pickled_data=pickle.dumps(notices).encode("base64")).save()
