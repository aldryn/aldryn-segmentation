# -*- coding: utf-8 -*-

import logging

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from aldryn_segmentation.segment_pool import segment_pool, SegmentOverride
from cms.toolbar.items import SubMenu

logger = logging.getLogger(__name__)


class SegmentationToolbarMiddleware(object):

    def process_request(self, request):
        # if hasattr(request, 'toolbar') and request.toolbar.edit_mode:
        self.create_segmentation_menu(request.toolbar)


    def create_segmentation_menu(self, toolbar):
        '''
        Using the SegmentPool, create a segmentation menu.
        '''
        segment_menu = toolbar.get_or_create_menu('aldryn-segmentation-menu', _('Segments'))
        pool = segment_pool.get_registered_segments()
        for segment_class in pool:
            segment_name = pool[segment_class]['name']

            segment_class_menu = segment_menu.get_or_create_menu(segment_class, segment_name)

            for config in pool[segment_class]['configurations']:
                override_state = pool[segment_class]['configurations'][config]['override']

                config_menu = SubMenu(config, None)
                segment_class_menu.add_item(config_menu)

                for override_label, override in [(_('Forced Active'), SegmentOverride.ForcedActive), (_('Forced Inactive'), SegmentOverride.ForcedInactive)]:

                    config_menu.add_ajax_item(
                        override_label,
                        action='http://127.0.0.1:8000/',
                        data={
                            'segment_class': segment_class,
                            'segment_config': config,
                            'override': override,
                            'value': (override == override_state)
                        },
                        active=(override == override_state),
                        on_success=toolbar.REFRESH_PAGE
                    )
