# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool

from .segment_plugin_base import SegmentPluginBase

from ..models import (
    AuthenticatedSegmentPluginModel,
    CookieSegmentPluginModel,
    FallbackSegmentPluginModel,
    SwitchSegmentPluginModel,
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


class SwitchSegmentPlugin(SegmentPluginBase):
    '''
    This switch segmentation plugin allows the operator to turn the segment ON
    or OFF statically and independently from the context. This is primarily
    useful for testing.
    '''

    model = SwitchSegmentPluginModel
    name = _('Segment by switch')

    # It doesn't make much sense to override this one...
    allow_overrides = False

    def is_context_appropriate(self, context, instance):
        return instance.on_off


class CookieSegmentPlugin(SegmentPluginBase):
    '''
    This is a segmentation plugin that renders output on the condition that a
    cookie with ``cookie_key`` is present and has the value ``cookie_value``.
    '''

    model = CookieSegmentPluginModel
    name = _('Segment by cookie')

    def is_context_appropriate(self, context, instance):
        request = context.get('request')
        value = request.COOKIES.get(instance.cookie_key)
        return (value == instance.cookie_value)


class AuthenticatedSegmentPlugin(SegmentPluginBase):
    '''
    This plugin allows segmentation based on the authentication/authorization
    status of the visitor.
    '''

    model = AuthenticatedSegmentPluginModel
    name = _('Segment by auth')

    def is_context_appropriate(self, context, instance):
        request = context.get('request')
        return request and request.user and request.user.is_authenticated()


plugin_pool.register_plugin(AuthenticatedSegmentPlugin)
plugin_pool.register_plugin(CookieSegmentPlugin)
plugin_pool.register_plugin(FallbackSegmentPlugin)
plugin_pool.register_plugin(SwitchSegmentPlugin)
