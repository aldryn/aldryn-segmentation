# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool

from ..models import SegmentLimitPluginModel
from .segment_plugin_base import SegmentPluginBase


class SegmentLimitPlugin(SegmentPluginBase):
    '''
    This is a special SegmentPlugin that acts as a top-level container for
    segmentation plugins and can set an upper-limit to the number of children
    that will be rendered in the current context.
    '''

    allow_children = True
    model = SegmentLimitPluginModel
    module = _('Segmentation')
    name = _('Limit Block')
    parent_classes = None
    render_template = 'aldryn_segmentation/_limiter.html'

    allow_overrides = False

    def render(self, context, instance, placeholder):
        context = super(SegmentLimitPlugin, self).render(
            context, instance, placeholder)
        context['child_plugins'] = self.get_context_appropriate_children(
            context, instance)
        return context

    def is_context_appropriate(self, context, instance):
        '''
        Returns True if any of its children are context-appropriate,
        else False.
        '''
        apt_children = self.get_context_appropriate_children(context, instance)
        num_apt = sum( 1 for child in apt_children if child[1] )
        return num_apt > 0

    def get_context_appropriate_children(self, context, instance):
        from ..segment_pool import SegmentOverride
        '''
        Returns a LIST OF TUPLES each containing a child plugin instance and a
        Boolean representing the plugin's appropriateness for rendering in
        this context.
        '''

        children = []
        # child_plugin_instances can sometimes be None
        generic_children = instance.child_plugin_instances or []
        render_all = (instance.max_children == 0)
        slots_remaining = instance.max_children

        for child_instance in generic_children:

            child_plugin = child_instance.get_plugin_class_instance()

            if child_plugin.model != child_instance.__class__:
                # If the child_instance's class does NOT
                # equal the registered plugin's model
                # then we're dealing with an orphan plugin.
                continue

            if render_all or slots_remaining > 0:

                if hasattr(child_plugin, 'is_context_appropriate'):
                    #
                    # This quacks like a segment plugin...
                    #
                    if (hasattr(child_plugin, 'allow_overrides') and
                            child_plugin.allow_overrides and
                            hasattr(child_plugin, 'get_segment_override')):

                        override = child_plugin.get_segment_override(
                            context, child_instance)

                        if override == SegmentOverride.ForcedActive:
                            child = (child_instance, True)
                        elif override == SegmentOverride.ForcedInactive:
                            child = (child_instance, False)
                        else:
                            #
                            # There's no override, so, just let the segment
                            # decide...
                            #
                            child = (
                                child_instance,
                                child_plugin.is_context_appropriate(
                                    context, child_instance
                                ),
                            )
                    else:
                        #
                        # Hmmm, this segment plugin appears to have no
                        # allow_overrides property or get_segment_override()
                        # method. OK then, let the plugin decide if it is
                        # appropriate to render.
                        #
                        child = (
                            child_instance,
                            child_plugin.is_context_appropriate(
                                context, child_instance
                            ),
                        )
                else:
                    #
                    # This doesn't quack like a Segment Plugin, so, it is
                    # always OK to render.
                    #
                    child =  ( child_instance, True, )

                if child[1]:
                    slots_remaining -= 1
            else:
                #
                # We've run out of available slots...
                #
                child = ( child_instance, False, )

            children.append(child)

        return children


plugin_pool.register_plugin(SegmentLimitPlugin)
