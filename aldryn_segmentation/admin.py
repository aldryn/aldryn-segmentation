# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf.urls import url
from django.contrib import admin

from .models import Segment
from .views import set_segment_override, reset_all_segment_overrides


class SegmentAdmin(admin.ModelAdmin):

    #
    # Note: model.Segment is empty and un-managed. Its sole purpose is to
    # provide the opportunity to add custom views to the AdminSite for
    # managing segments from the toolbar.
    #

    def get_model_perms(self, request):
        '''
        Returns an empty perms dict which has the effect of disabling its
        display in the AdminSite, but still allows access to the views defined
        below.
        '''
        return dict()

    def get_urls(self):

        return [
            url(r'set_override/$',
                self.admin_site.admin_view(set_segment_override),
                name='set_segment_override'
            ),

            url(r'reset_all_segment_overrides/$',
                self.admin_site.admin_view(reset_all_segment_overrides),
                name='reset_all_segment_overrides'
            ),
        ] + super(SegmentAdmin, self).get_urls()


admin.site.register(Segment, SegmentAdmin)
