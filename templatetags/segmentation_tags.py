# -*- coding: utf-8 -*-

import logging

from django import template

from classytags.helpers import InclusionTag
from classytags.core import Options
from classytags.arguments import Argument

from ..segment_pool import SegmentOverride

register = template.Library()
logger = logging.getLogger(__name__)


class RenderSegmentPlugin(InclusionTag):
    template = 'cms/content.html'
    name = 'render_segment_plugin'
    options = Options(
        Argument('plugin'),
        Argument('render_plugin')
    )

    @classmethod
    def is_renderable(cls, context, plugin_instance):
        child_plugin = plugin_instance.get_plugin_class_instance()

        if hasattr(child_plugin, 'is_context_appropriate'):
            # This is a segment plugin... or at least quacks like one.
            if child_plugin.allow_overrides and hasattr(child_plugin, 'get_segment_override'):
                override = child_plugin.get_segment_override(plugin_instance)
                if override == SegmentOverride.ForcedActive:
                    return True
                elif override == SegmentOverride.ForcedInactive:
                    return False

            # OK, what does is_context_appropriate say?
            return child_plugin.is_context_appropriate(context, plugin_instance)

        # This doesn't quack like a SegmentPlugin, so, it always renders.
        return True


    def get_context(self, context, plugin, render_plugin):

        #
        # NOTE: This code should be more or less identical to that of
        # cms.templatetags.cms_tags.RenderPlugin()
        # --------------------------------------------------------------------
        edit = False
        if not plugin:
            return {'content': ''}
        request = context['request']
        toolbar = getattr(request, 'toolbar', None)
        page = request.current_page
        if toolbar and toolbar.edit_mode and (not page or page.has_change_permission(request)):
            edit = True
        if edit:
            from cms.middleware.toolbar import toolbar_plugin_processor

            processors = (toolbar_plugin_processor,)
        else:
            processors = None
        # --------------------------------------------------------------------
        # End of duplicate code
        #

        plugin_instance = plugin  # This makes more sense, no?
        plugin = plugin_instance.get_plugin_class_instance()

        if not (render_plugin and self.is_renderable(context, plugin_instance)):
            #
            # OK, this is a Segmentation Plugin that is NOT appropriate for
            # rendering in the current context. Unfortunately, we need to
            # render the plugin, but throw away the results in order to allow
            # the structureboard to display properly. Ugly!
            #
            plugin_instance.render_plugin(context, processors=processors)
            return {'content': ''}

        #
        # Either this isn't a Segmentation Plugin OR, it is and it is
        # appropriate for rendering in this context. Proceed as usual.
        #
        return {'content': plugin_instance.render_plugin(context, processors=processors)}


register.tag(RenderSegmentPlugin)