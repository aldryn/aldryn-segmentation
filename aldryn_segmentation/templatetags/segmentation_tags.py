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

        # TODO: Seems to me this method is not necessary
        # Once tests are established then maybe we can remove this.

        child_plugin = plugin_instance.get_plugin_class_instance()

        try:
            allow_overrides = child_plugin.allow_overrides
            get_override = child_plugin.get_segment_override
        except AttributeError:
            # This doesn't quack like a SegmentPlugin, so, it always renders.
            return True

        # This is a segment plugin... or at least quacks like one.
        if allow_overrides:
            # only evaluate override if we allow overrides
            override = get_override(context, plugin_instance)

            if override == SegmentOverride.ForcedActive:
                return True
            elif override == SegmentOverride.ForcedInactive:
                return False

        # OK, what does the plugin's is_context_appropriate() say?
        return child_plugin.is_context_appropriate(context, plugin_instance)

    def get_context(self, context, plugin, render_plugin):
        response = super(RenderSegmentPlugin, self).get_context(context, plugin)

        if not (render_plugin and self.is_renderable(context, plugin)):
            # OK, this is a Segmentation Plugin that is NOT appropriate for
            # rendering in the current context. Unfortunately, we need to
            # render the plugin, but throw away the results in order to allow
            # the structureboard to display properly. Ugh!
            response['content'] = ''
        return response


register.tag(RenderSegmentPlugin)
