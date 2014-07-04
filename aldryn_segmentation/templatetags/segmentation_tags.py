# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template

from classytags.core import Options
from classytags.arguments import Argument

from cms.templatetags.cms_tags import RenderPlugin

from ..segment_pool import SegmentOverride


register = template.Library()


class RenderSegmentPlugin(RenderPlugin):
    name = 'render_segment_plugin'
    options = Options(
        Argument('plugin'),
        Argument('render_plugin')
    )

    def is_renderable(self, context, plugin_instance):
        '''
        Determines whether this plugin is to be rendered in this context.
        '''

        child_plugin = plugin_instance.get_plugin_class_instance()
        if (hasattr(child_plugin, 'allow_overrides') and
                hasattr(child_plugin, 'is_context_appropriate')):
            #
            # This is a segment plugin... or at least quacks like one.
            #
            if (child_plugin.allow_overrides and
                    hasattr(child_plugin, 'get_segment_override')):
                override = child_plugin.get_segment_override(
                    context, plugin_instance)
                
                if override == SegmentOverride.ForcedActive:
                    return True
                elif override == SegmentOverride.ForcedInactive:
                    return False

            #
            # OK, what does the plugin's is_context_appropriate() say?
            #
            return child_plugin.is_context_appropriate(context, plugin_instance)
        #
        # This doesn't quack like a SegmentPlugin, so, it always renders.
        #
        return True

    #
    # TODO: Once Aldryn gets updated to 3.0.3 or later, remove this block!
    #
    def get_processors(self, context, plugin):
        #
        # Prepend frontedit toolbar output if applicable. Moved to its own
        # method to aide subclassing the whole RenderPlugin if required.
        #
        edit = False
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
        return processors


    def get_context(self, context, plugin, render_plugin):

        if not plugin:
            return {'content': ''}

        plugin_instance = plugin
        plugin = plugin_instance.get_plugin_class_instance()

        processors = self.get_processors(context, plugin)

        if not (render_plugin and self.is_renderable(context, plugin_instance)):
            #
            # OK, this is a Segmentation Plugin that is NOT appropriate for
            # rendering in the current context. Unfortunately, we need to
            # render the plugin, but throw away the results in order to allow
            # the structureboard to display properly. Ugh!
            #
            plugin_instance.render_plugin(context, processors=processors)
            return {'content': ''}

        #
        # Either this isn't a Segmentation Plugin OR, it is and it is
        # appropriate for rendering in this context. Proceed as usual.
        #
        return {'content': plugin_instance.render_plugin(
            context, processors=processors)}


register.tag(RenderSegmentPlugin)