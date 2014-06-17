# -*- coding: utf-8 -*-

import logging

from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from ..models import SegmentLimitPluginModel

logger = logging.getLogger(__name__)


class SegmentLimitPlugin(CMSPluginBase):
    '''
    This is a special SegmentPlugin that acts as a top-level container for
    segmentation plugins and can set an upper-limit to the number of children
    that will be rendered in the current context.
    '''

    allow_children = True
    cache = False
    model = SegmentLimitPluginModel
    module = _('Segmentation')
    name = _('Limit Block')
    render_template = 'aldryn_segmentation/_limiter.html'
    text_enabled = False

    def render(self, context, instance, placeholder):
        context = super(SegmentLimitPlugin, self).render(context, instance, placeholder)
        context['child_plugins'] = self.get_context_appropriate_children(context, instance)
        return context

    def get_context_appropriate_children(self, context, instance):
        '''
        Returns a LIST OF TUPLES each containing a child plugin instance and a
        Boolean representing the plugin's appropriateness for rendering in
        this context.
        '''

        children = []
        render_all = (instance.max_children == 0)
        slots_remaining = instance.max_children

        for child_instance in instance.child_plugin_instances:

            child_plugin = child_instance.get_plugin_class_instance()

            if render_all or slots_remaining > 0:
                #
                # We're allowing all 'ducks' here, but it may make sense to
                # instead use isinstance(...)
                #
                if hasattr(child_plugin, 'is_context_appropriate'):
                    # This is a segmentation plugin.
                    child = (child_instance, child_plugin.is_context_appropriate(context, child_instance), )
                else:
                    # This is a normal plugin. It is always OK to render.
                    child =  ( child_instance, True, )

                if child[1]:
                    slots_remaining -= 1
            else:
                # We've run out of available slots...
                child = ( child_instance, False, )

            children.append(child)

        # logger.debug(u'In this context, these child plugins seem appropriate: %s' % [child for child in children if child[1]])
        return children

plugin_pool.register_plugin(SegmentLimitPlugin)
