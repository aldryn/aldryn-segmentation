# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin

from .models import Segment
from .views import set_segment_override, reset_all_segment_overrides

class SegmentAdmin(admin.ModelAdmin):

    '''
    Note: model.Segment is empty and unmanaged. Its sole purpose is to provide
    the opportunity to add custom views to the AdminSite for managing segments
    from the toolbar.
    '''

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