# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


class SetCookiePluginModel(CMSPlugin):

    class Meta:
        app_label = 'aldryn_segmentation'

    EXPIRATION_CHOICES = (
        ( -1, _('Delete cookie'), ),
        (  0, _('Session-only cookie'), ),
        (  1, _('1 day'), ),
        (  7, _('1 week'), ),
        ( 30, _('30 days'), ),
        (365, _('1 year'), ),
    )

    key = models.CharField(_(u'cookie key'),
        blank=True,
        help_text=_(u'The key for the cookie to set.'),
        max_length=64,
    )

    value = models.CharField(_(u'cookie value'),
        blank=True,
        help_text=_(u'The value for the cookie to set'),
        max_length=64,
    )

    overwrite = models.BooleanField(_(u'overwrite existing?'),
        default=False,
        help_text=_(u'Check this box to overwrite/update an existing cookie with the same key with new value/expiration/path'),
    )

    days_to_expire = models.SmallIntegerField(_(u'days to expire'),
        choices=EXPIRATION_CHOICES,
        default=365,
        help_text=_(u'When should this cookie expire?'),
    )

    path = models.CharField(_(u'path'),
        blank=True,
        default='/',
        max_length=255
    )

    def __unicode__(self):
        return u'“{key}” to “{value}”'.format(
            key=self.key,
            value=self.value
        )
