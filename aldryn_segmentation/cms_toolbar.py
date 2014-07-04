# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool

from .segment_pool import segment_pool


@toolbar_pool.register
class SegmentToolbar(CMSToolbar):

    def populate(self):

        segment_pool.get_segments_toolbar_menu(
            self.request.user,
            self.request.toolbar,
            csrf_token=self.request.COOKIES.get('csrftoken')
        )
