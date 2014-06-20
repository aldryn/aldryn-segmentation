# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.toolbar.items import SubMenu, Break, AjaxItem

from .segment_pool import segment_pool, SegmentOverride



@toolbar_pool.register
class SegmentToolbar(CMSToolbar):

    def populate(self):

        self.create_segmentation_menu(
            self.request.user,
            self.request.toolbar,
            csrf_token=self.request.COOKIES.get('csrftoken')
        )


    def create_segmentation_menu(self, user, toolbar, csrf_token):
        '''
        Using the SegmentPool, create a segmentation menu.
        '''

        # NOTE: This is a list of tuples now...
        pool = segment_pool.get_registered_segments()

        num_overrides = segment_pool.get_num_overrides_for_user(user)

        segment_menu_name = _('Segments (%s)' % num_overrides) if num_overrides else _('Segments')
        segment_menu = toolbar.get_or_create_menu(
            'segmentation-menu',
            segment_menu_name
        )

        for segment_class_name, segment_class in pool:
            segment_name = segment_class['NAME']

            segment_class_menu = segment_menu.get_or_create_menu(
                segment_class_name,
                segment_name
            )

            for config_str, config in segment_class['CONFIGURATIONS']:

                user_override = segment_pool.get_override_for_segment(
                    user,
                    segment_class_name,
                    config_str
                )

                config_menu = SubMenu(config_str, csrf_token)
                segment_class_menu.add_item(config_menu)

                for override, override_label in SegmentOverride.overrides_list:
                    if override == SegmentOverride.NoOverride:
                        # We don't really want to show the 'No override' as an
                        # actionable item.
                        continue

                    active = bool(override == user_override)

                    if active:
                        # Mark parent menus active too
                        config_menu.active = True
                        segment_class_menu.active = True

                    if (override != user_override):
                        override_value = override
                    else:
                        override_value = SegmentOverride.NoOverride

                    config_menu.add_ajax_item(
                        override_label,
                        action=reverse('admin:set_segment_override'),
                        data={
                            'segment_class': segment_class_name,
                            'segment_config': config_str,
                            'override': override_value,
                        },
                        active=active,
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
