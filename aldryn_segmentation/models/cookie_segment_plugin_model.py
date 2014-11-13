# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils import six
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _

from .base import SegmentBasePluginModel


class CookieSegmentPluginModel(SegmentBasePluginModel):

    class Meta:
        app_label = 'aldryn_segmentation'

    #
    # Consider that we should probably support either:
    #   Simple wildcard '*', '?' expressions or
    #   RegEx expressions or
    #   Both.
    #
    # A note about the max_lengths selected: browsers can support up to 4093
    # characters for a given cookie (combining both the key and the value). So
    # either one can be up to 4092 chars in length. Since these are
    # implemented as VarChars, this shouldn't be too wasteful and still
    # support almost anything.
    #
    # NOTE: This forces a requirement for MySQL users to be using 5.0.3 or
    # later (which is already a requirement for Django 1.5+).
    #

    cookie_key = models.CharField(_('name of cookie'),
        blank=False,
        default='',
        help_text=_('Name of cookie to consider.'),
        max_length=4096,
    )

    cookie_value = models.CharField(_('value to compare'),
        blank=False,
        default='',
        help_text=_('Value to consider.'),
        max_length=4096,
    )

    @property
    def configuration_string(self):

        def wrapper():
            return _('“{key}” equals “{value}”').format(key=self.cookie_key, value=self.cookie_value)

        return lazy(
            wrapper,
            six.text_type
        )()


