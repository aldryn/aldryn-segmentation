# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool

from ..cms_plugins import SegmentPluginBase

from ..models import (
    CookieSegmentPluginModel,
    FallbackSegmentPluginModel,
    SwitchSegmentPluginModel,
    CountrySegmentPluginModel,
)


class FallbackSegmentPlugin(SegmentPluginBase):
    '''
    This segment plugin represents a degenerate case where the segment
    always matches.
    '''

    model = FallbackSegmentPluginModel
    name = _('Fallback')

    # It doesn't make much sense to override this one...
    allow_overrides = False

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

    # It doesn't make much sense to override this one...
    allow_overrides = False

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

    #
    # TODO: Move this and related bits to another repo
    #

    model = CountrySegmentPluginModel
    name = _('Segment by Country')

    def is_context_appropriate(self, context, instance):
        code = context.get('COUNTRY_CODE')
        return (code == instance.country_code)

plugin_pool.register_plugin(CountrySegmentPlugin)
