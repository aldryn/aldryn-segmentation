# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from cms.toolbar.utils import get_toolbar_from_request
from django import template

from cms.templatetags import cms_tags


register = template.Library()


@register.simple_tag(takes_context=True)
def render_segment_plugin(context, plugin, render_plugin):
    request = context['request']
    toolbar = get_toolbar_from_request(request)
    if toolbar.uses_legacy_structure_mode:
        # We need to handle it the old way. Render ALL plugins on the page so
        # that the legacy structure board can display all of them.
        rendered = cms_tags.render_plugin(context, plugin)
        if render_plugin:
            return rendered
        else:
            # We had to render the plugin and all its sub-plugins above and
            # so that the legacy structure board sees the invisible plugins.
            # (js via sekizai).
            # We return nothing as content though, since the plugin should not
            # be visible.
            return ''
    else:
        # The new way. yay!
        # The structure including all the hidden plugins is handled
        # entirely separate. So we don't have to worry about it here.
        # We only need to render plugins that are actually visible.
        if render_plugin:
            return cms_tags.render_plugin(context, plugin)
        else:
            # FIXME: hmmm... why does the popup not work if the plugin is not
            #        rendered? It should work without it.
            cms_tags.render_plugin(context, plugin)
            return ''
