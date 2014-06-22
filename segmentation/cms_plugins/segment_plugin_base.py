# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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
    parent_classes = ['SegmentLimitPlugin', ]
    render_template = 'segmentation/_segment.html'
    text_enabled = False

    #
    # Leave set to True to allow this plugin to be displayed in the Segment
    # Toolbar Menu for overriding by the operator.
    #
    allow_overrides = True


    def get_segment_override(self, context, instance):
        '''
        If the current user is logged-in and this segment plugin allows
        overrides, then return the current override for this segment, else,
        returns SegmentOverride.NoOverride.

        This should NOT be overridden in subclasses.
        '''

        # This can't be defined at the file level, else circular imports
        from ..segment_pool import segment_pool, SegmentOverride

        request = context['request']
        if request.user.is_authenticated():
            return segment_pool.get_override_for_segment(
                request.user, self, instance
            )

        return SegmentOverride.NoOverride


    def is_context_appropriate(self, context, instance):
        '''
        Return True if this plugin is appropriate for rendering in the given
        context. (Non-degenerate) Segment Plugins should override this and
        supply the appropriate tests.
        '''

        return True
