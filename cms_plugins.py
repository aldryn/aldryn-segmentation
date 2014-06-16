# -*- coding: utf-8 -*-

import logging

from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from cms.models import CMSPlugin

from .models import (
    CookieSegmentPluginModel,
    SegmentLimitPluginModel,
    SwitchSegmentPluginModel,
    CountrySegmentPluginModel,
)

logger = logging.getLogger(__name__)

class SegmentPluginBase(CMSPluginBase):

    '''
    Abstract base class to be used for all Segment (and Limit) Plugins. It
    provides the default implementation of necessary additional methods for:

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
    parent_classes = []  # Can go anywhere...
    render_template = 'aldryn_segmentation/_limiter.html'

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


class FallbackSegmentPlugin(SegmentPluginBase):

    '''
    This segment plugin represents a degenerate case where the segment
    always matches.
    '''

    model = CMSPlugin
    name = _('Fallback')
    render_template = 'aldryn_segmentation/_segment.html'

    def is_context_appropriate(self, context, instance):
        return True

plugin_pool.register_plugin(FallbackSegmentPlugin)


class SwitchSegmentPlugin(SegmentPluginBase):
    '''
    This switch segmentation plugin allows the operator to turn the segment ON
    or OFF statically and independently from the context. This is primarily
    useful for testing.
    '''
    model = SwitchSegmentPluginModel
    name = _('Segment by Switch')

    def is_context_appropriate(self, context, instance):
        return instance.on_off

plugin_pool.register_plugin(SwitchSegmentPlugin)


class CookieSegmentPlugin(SegmentPluginBase):
    '''
    This is a segmentation plugin that renders output on the condition that a
    cookie with ``cookie_key`` is present and has the value ``cookie_value``.
    '''
    model = CookieSegmentPluginModel
    name = _('Segment by Cookie')

    def is_context_appropriate(self, context, instance):
        request = context.get('request')
        value = request.COOKIES.get(instance.cookie_key)
        return (value == instance.cookie_value)

plugin_pool.register_plugin(CookieSegmentPlugin)


class CountrySegmentPlugin(SegmentPluginBase):

    '''
    This plugin allows segmentation based on the visitor's IP addresses
    associated country code. Use of this segment requires the use of the
    'resolve_country_code_middleware' provided in this distribution. This
    middleware, in turn, depends on django.contrib.geo_ip and MaxMind's
    GeoLite dataset or similar.
    '''

    model = CountrySegmentPluginModel
    name = _('Segment by Country')

    def is_context_appropriate(self, context, instance):
        code = context.get('COUNTRY_CODE')
        return (code == instance.country_code)

plugin_pool.register_plugin(CountrySegmentPlugin)
