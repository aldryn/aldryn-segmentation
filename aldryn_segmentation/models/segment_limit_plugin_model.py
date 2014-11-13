# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.translation import ugettext_lazy as _, string_concat

from cms.models import CMSPlugin


#
# NOTE: The SegmentLimitPluginModel does NOT subclass SegmentBasePluginModel
#
@python_2_unicode_compatible
class SegmentLimitPluginModel(CMSPlugin):

    class Meta:
        app_label = 'aldryn_segmentation'

    #
    # Need to consider how best to display this in the Plugin Change Form...
    #
    #   0 means "Display ALL segments that match",
    #   1 means "Display first matching segment",
    #   2 means "Display up to two matching segments,"
    #     and so on...
    #

    label = models.CharField(_('label'),
        blank=True,
        default='',
        help_text=_('Optionally set a label for this limit block.'),
        max_length=128,
    )

    max_children = models.PositiveIntegerField(_('# of matches to display'),
        blank=False,
        default=1,
        help_text=_('Display up to how many matching segments?'),
    )

    @property
    def configuration_string(self):
        if self.max_children == 0:
            return _('Show All')
        elif self.max_children == 1:
            return _('Show First')
        else:
            return string_concat(_('Show First'), ' ', self.max_children)


    def __str__(self):
        '''
        If there is a label, show that with the configuration in brackets,
        otherwise, just return the configuration string.
        '''

        if self.label:
            conf_str = _('{label} [{config}]').format(
                label=self.label,
                config=force_text(self.configuration_string),
            )
        else:
            conf_str = self.configuration_string

        return force_text(conf_str)
