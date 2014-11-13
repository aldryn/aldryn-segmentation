# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .base import SegmentBasePluginModel


class SwitchSegmentPluginModel(SegmentBasePluginModel):

    class Meta:
        app_label = 'aldryn_segmentation'

    on_off = models.BooleanField(_('Always on?'),
        default=True,
        help_text=_('Uncheck to always hide child plugins.'),
    )

    @property
    def configuration_string(self):
        if self.on_off:
            return _('Always ON')
        else:
            return _('Always OFF')


