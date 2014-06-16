# -*- coding: utf-8 -*-

import logging

from django import template

from classytags.helpers import InclusionTag
from classytags.core import Options
from classytags.arguments import Argument

register = template.Library()
logger = logging.getLogger(__name__)


class RenderSegmentPlugin(InclusionTag):
    template = 'cms/content.html'
    name = 'render_segment_plugin'
    options = Options(
        Argument('plugin'),
        Argument('render_plugin')
    )

    def get_context(self, context, plugin, render_plugin):
        logger.debug('RenderSegmentPlugin received: %s and %s' % ( plugin, render_plugin, ))
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

        plugin_instance = plugin  # This makes more sense, no?
        plugin = plugin_instance.get_plugin_class_instance()
        if not render_plugin or hasattr(plugin, 'is_context_appropriate') and not plugin.is_context_appropriate(context, plugin_instance):
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