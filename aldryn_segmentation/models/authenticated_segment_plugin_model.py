# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .base import SegmentBasePluginModel


class AuthenticatedSegmentPluginModel(SegmentBasePluginModel):

    class Meta:
        app_label = 'aldryn_segmentation'

    @property
    def configuration_string(self):
        return _('is Authenticated')


