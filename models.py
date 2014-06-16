# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


class SegmentLimitPluginModel(CMSPlugin):

    #
    # This is an awkward input, consider using a UI widget that makes better
    # sense of this.
    #
    #   0 means "Display ALL segments that match",
    #   1 means "Display first matching segment",
    #   2 means "Display up to two matching segments,"
    #     and so on...
    #
    label = models.CharField(_('block label'),
        blank=False,
        default='',
        help_text=_('Optionally provide a label for this block.'),
        max_length=128,
    )

    max_children = models.PositiveIntegerField(_('# of matches to display'),
        blank=False,
        default=1,
        help_text=_('Display up to how many matching segments?'),
    )

    def __unicode__(self):
        if self.max_children == 0:
            config = u'Show All'
        elif self.max_children == 1:
            config = u'Show First'
        else:
            config = u'Show First %d' % self.max_children
        if self.label:
            return u'%s [%s]' % (self.label, config, )
        else:
            return config


class SwitchSegmentPluginModel(CMSPlugin):

    on_off = models.BooleanField(_('Always on?'),
        default=True,
        help_text=_('Uncheck to always hide child plugins.'),
    )

    def __unicode__(self):
        if self.on_off:
            return u'Always ON'
        else:
            return u'Always OFF'


class CookieSegmentPluginModel(CMSPlugin):

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
    label = models.CharField(_('segment label'),
        blank=False,
        default='',
        help_text=_('Optionally provide a label for this segment.'),
        max_length=128,
        null=True,
    )

    cookie_key = models.CharField(_('name of cookie'),
        blank=False,
        default='*',
        help_text=_('Name of cookie to consider.'),
        max_length=4096,
    )

    cookie_value = models.CharField(_('value to compare'),
        blank=False,
        default='*',
        help_text=_('Value to consider.'),
        max_length=4096,
    )

    def __unicode__(self):
        if self.label:
            return self.label
        else:
            return u'cookie: %s has value: %s' % (self.cookie_key, self.cookie_value, )


class CountrySegmentPluginModel(CMSPlugin):

    label = models.CharField(_('segment label'),
        blank=False,
        default='',
        help_text=_('Optionally provide a label for this segment.'),
        max_length=128,
        null=True,
    )

    country_code = models.CharField(_('country code'),
        blank=False,
        default='',
        help_text=_('Provide the 2-letter ISO country code'),
        max_length=2,
    )

    def __unicode__(self):
        if self.label:
            return self.label
        else:
            return u'country code is %s' % (self.country_code, )
