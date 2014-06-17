# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from cms.plugin_base import CMSPluginBase

class SegmentPluginBase(CMSPluginBase):
    '''
    Abstract base class to be used for all segment plugins. It provides the
    default implementation of necessary additional methods for:

        * Registering conditions for Segmentation Previews for operators;
        * Reporting if the segment's condition(s) are met.

    Also, by using this base class, the Segmentation Group Plugin will be able
    accept the plugin (The Segmentation Group plugin has child_classes set to
    this class).
    '''

    class Meta:
        abstract = True

    allow_children = True
    cache = False
    module = _('Segmentation')
    render_template = 'aldryn_segmentation/_segment.html'
    text_enabled = False

    #
    # This is a new property. Leave set to True to allow this plugin to be
    # displayed in the Segment Menu for overriding by the operator.
    #
    allow_overrides = True


    def is_context_appropriate(self, context, instance):
        '''
        Return True if this plugin is appropriate for rendering in the given
        context. (Non-degenerate) Segment Plugins should override this and
        supply the appropriate tests.
        '''

        #
        # NOTE: The 'context' argument above will contain a PluginContext.
        # PluginContexts are subclassed from Context. See:
        # cms.plugin_rendering.py for the PluginContext implementation.
        #

        return True
