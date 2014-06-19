# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.toolbar.items import SubMenu, Break, AjaxItem

from ..segment_pool import segment_pool, SegmentOverride


class SegmentationToolbarMiddleware(object):

    def process_request(self, request):
        if hasattr(request, 'toolbar'):
            self.create_segmentation_menu(request.toolbar, csrf_token=request.COOKIES.get('csrftoken'))


    # TODO: Add support for operator-specific overrides
    # TODO: Won't this all work in a cms_toolbar.py file rather than in MW?
    # TODO: We should move pool-implementation-specific logic back to the pool.
    def create_segmentation_menu(self, toolbar, csrf_token):
        '''
        Using the SegmentPool, create a segmentation menu.
        '''

        pool = segment_pool.get_registered_segments()

        #
        # Count the number of current overrides...
        #
        num_overrides = 0
        for segment_class in pool.itervalues():
            for config in segment_class['CONFIGURATIONS'].itervalues():
                override_state = int(config['OVERRIDES'])
                if override_state != SegmentOverride.NoOverride:
                    num_overrides += 1

        segment_menu_name = _('Segments (%s)' % num_overrides) if num_overrides else _('Segments')
        segment_menu = toolbar.get_or_create_menu('segmentation-menu', segment_menu_name)

        for segment_class in pool:
            segment_name = pool[segment_class]['NAME']

            segment_class_menu = segment_menu.get_or_create_menu(segment_class, segment_name)

            for config in pool[segment_class]['CONFIGURATIONS']:
                override_state = int(pool[segment_class]['CONFIGURATIONS'][config]['OVERRIDES'])

                config_menu = SubMenu(config, csrf_token)
                segment_class_menu.add_item(config_menu)

                for override_label, override in [(_('Forced Active'), SegmentOverride.ForcedActive), (_('Forced Inactive'), SegmentOverride.ForcedInactive)]:

                    config_menu.add_ajax_item(
                        override_label,
                        action=reverse('admin:set_segment_override'),
                        data={
                            'segment_class': segment_class,
                            'segment_config': config,
                            'override': override,
                            'value': (override != override_state),
                        },
                        active=bool(override == override_state),
                        on_success=toolbar.REFRESH_PAGE
                    )

        segment_menu.add_item(Break())
        reset_ajax_item = AjaxItem(
            _('Reset all segments'),
            action=reverse('admin:reset_all_segment_overrides'),
            csrf_token=csrf_token,
            data={},
            disabled=bool(num_overrides == 0),
            on_success=toolbar.REFRESH_PAGE
        )
        segment_menu.add_item(reset_ajax_item)
