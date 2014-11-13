# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from ..forms import SetCookieAdminForm
from ..models import SetCookiePluginModel


class SetCookiePlugin(CMSPluginBase):
    form = SetCookieAdminForm
    name = u'Set Cookie'
    model = SetCookiePluginModel
    module = _('Segmentation')
    render_template = "aldryn_segmentation/set_cookie_plugin.html"
    text_enabled = False

    fieldsets = (
        (None, {
            'fields': (
                ('key', 'value', 'setting', ),
                'days_to_expire',
                ('path_choice', 'original_referer', ),
                'overwrite',
            ),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        AdminForm = super(SetCookiePlugin, self).get_form(request, obj, **kwargs)

        class SetCookiePluginAdminForm(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return SetCookiePluginAdminForm

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        context['placeholder'] = instance
        return context

plugin_pool.register_plugin(SetCookiePlugin)