# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


@python_2_unicode_compatible
class Segment(models.Model):
    '''
    This is a hollow, unmanaged model that simply allows us to attach custom
    admin views into the AdminSite.
    '''

    class Meta:
        app_label = 'aldryn_segmentation'
        managed=False

    def __str__(self):
        return 'Segment is an empty, unmanaged model.'


@python_2_unicode_compatible
class SegmentBasePluginModel(CMSPlugin):
    
    #
    # Defines a common interface for segment plugins. Also note that plugin
    # model's subclassing this class will automatically be (un-)registered
    # (from)to the segment_pool via 'pre_delete' and 'post_save' signals. This
    # is implemented in aldryn_segmentation.segment_pool.
    #

    class Meta:
        abstract = True
        app_label = 'aldryn_segmentation'


    label = models.CharField(_('label'),
        blank=True,
        default='',
        max_length=128,
    )


    @property
    def configuration_string(self):
        '''
        Return a ugettext_lazy object (or a lazy function that returns the
        same) that represents the configuration for the plugin instance in a
        unique, concise manner that is suitable for a toolbar menu option.

        Some Examples:
            Cookie:
                '"key" equals "value"'
            Country:
                'Country is Kenya'
            Auth:
                'User is authenticated'
            Switch:
                'Always ON'
            Limit:
                'Show First'

        In cases where the returned string is composed with placeholders, E.g.:

            Cookie:
                ugettext_lazy('“{key}” equals “{value}”').format(
                    key=self.key,
                    value=self.value
                )

        You *must* actually return a evaluated, lazy wrapper around the
        gettext_lazy operation as follows:

            def configuration_string(self):
                wrapper():
                    return ugettext_lazy('“{key}” equals “{value}”').format(
                        key=self.key,
                        value=self.value
                    )

                # NOTE: the trailing '()'
                return lazy(wrapper, six.text_type)()

        Otherwise, the translations won't happen.

        This construction is not required for untranslated or non-
        parameterized translations.


        NOTE: Each subclass must override to suit.
        '''
        raise NotImplementedError("Please Implement this method")


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