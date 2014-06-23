# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import warnings

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils import six
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.functional import Promise
from django.utils.translation import activate, get_language, ugettext_lazy as _

from cms.exceptions import PluginAlreadyRegistered, PluginNotRegistered
from cms.plugin_pool import plugin_pool
from cms.toolbar.items import SubMenu, Break, AjaxItem

from ..cms_plugins import SegmentPluginBase
from ..models import SegmentBasePluginModel


#
# A simple enum so we can use the same code in Python's < 3.4.
#
class SegmentOverride:
    NoOverride, ForcedActive, ForcedInactive = range(3)

    overrides_list = [
        (NoOverride, _('No override')),
        (ForcedActive, _('Forced active')),
        (ForcedInactive, _('Forced inactive')),
    ]


@python_2_unicode_compatible
class SegmentPool(object):
    '''
    This maintains a set of nested sorted dicts containing, among other
    attributes, a list of segment plugin instances in the form:

    segments = {
        /class/ : {
            NAME: _(/name/),
            CFGS: {
                /configuration_string/ : {
                    LABEL: _(/configuration_string/),
                    OVERRIDES: {
                        /user.id/: /SegmentOverride enum value/,
                        ...
                    },
                    INSTANCES: [ ... ]
                }
            }
        }
    }

    The outer-most dict organizes everything by the class name of the plugin.
    The actual human-readable version of the plugin's type name is stored
    under the key 'NAME'.

    Each plugin's unique configuration is stored in the plugin type's CFGS
    dict keyed with the instance's configuration_string realised as 'en'
    unicode. The unresolved version of the string--usually a lazy translation
    proxy object--is stored under the configuration's 'LABEL' key. This allows
    translation to any other language (that is in the gettext catalog) at
    will. This is also used for correctly sorting the configurations in the
    current language.

    This is implmented as a non-persistent, system-wide singleton, it is
    shared by all operators of the system. In order to keep overrides for each
    user distinct, they are stored in the OVERRIDES dict, keyed with the
    user's username.

    Plugin instances are recorded in the INSTANCES list. As well as allowing
    us to find instances that have changed their configuration (likely to
    happen when an operator changes the plugin's configuration), this allows
    us to prune no-longer relevant parts of this structure as instances are
    de-registered.
    '''

    #
    # Magic Strings for managing the structures below.
    #
    CFGS = 'CFGS'
    NAME = 'NAME'
    LABEL = 'LABEL'
    OVERRIDES = 'OVERRIDES'
    INSTANCES = 'INSTANCES'


    def __init__(self):
        self.segments = dict()
        self._sorted_segments = dict()
        self.discover()


    def discover(self):
        '''
        Find and register any SegmentPlugins already configured in the CMS and
        register them...
        '''

        for plugin_class in plugin_pool.get_all_plugins():
            #
            # NOTE: We're not looking for ducks here. Should we be?
            #
            if (issubclass(plugin_class, SegmentPluginBase) and
                    plugin_class.allow_overrides):
                for plugin_instance in plugin_class.model.objects.all():
                    self.register_segment_plugin(plugin_instance)


    def register_segment_plugin(self, plugin_instance):
        '''
        Registers the provided plugin_instance into the SegmentPool.
        Raises:
            PluginAlreadyRegistered: if the plugin is already registered and
            ImproperlyConfigured: if not an appropriate type of plugin.

        Note: plugin_instance.configuration_string can return either of:

        1. A number string of text
        2. A lazy translation object (Promise)
        '''

        if isinstance(plugin_instance, SegmentBasePluginModel):
            plugin_class_instance = plugin_instance.get_plugin_class_instance()

            if plugin_class_instance.allow_overrides:
                #
                # There is no need to register a plugin that doesn't
                # allow overrides.
                #
                plugin_class_name = plugin_class_instance.__class__.__name__
                plugin_name = plugin_class_instance.name

                if plugin_class_name not in self.segments:
                    self.segments[plugin_class_name] = {
                        self.NAME: plugin_name,
                        self.CFGS: dict(),
                    }
                    self._sorted_segments = dict()
                segment_class = self.segments[plugin_class_name]

                plugin_config = plugin_instance.configuration_string

                #
                # NOTE: We always use the 'en' version of the configuration string
                # as the key.
                #
                lang = get_language()
                activate('en')

                if isinstance(plugin_config, Promise):
                    plugin_config_key = force_text(plugin_config)
                elif isinstance(plugin_config, six.text_type):
                    plugin_config_key = plugin_config
                else:
                    warnings.warn('register_segment: Not really sure what '
                                '‘plugin_instance.configuration_string’ returned!')

                activate(lang)

                segment_configs = segment_class[self.CFGS]

                if plugin_config_key not in segment_configs:
                    # We store the un-translated version as the LABEL
                    segment_configs[plugin_config_key] = {
                        self.LABEL : plugin_config,
                        self.OVERRIDES : dict(),
                        self.INSTANCES : list(),
                    }
                    self._sorted_segments = dict()

                segment = segment_configs[plugin_config_key]

                if plugin_instance not in segment[self.INSTANCES]:
                    segment[self.INSTANCES].append( plugin_instance )
                    self._sorted_segments = dict()
                else:
                    cls = plugin_instance.get_plugin_class_instance().__class__.__name__
                    raise PluginAlreadyRegistered('The segment plugin {0} cannot '
                        'be registered because it already is.'.format(cls))

        else:
            try:
                cls = plugin_instance.get_plugin_class_instance().__class__.__name__
                raise ImproperlyConfigured('Segment Plugins must subclasses of '
                    'SegmentBasePluginModel. {0!r} is not.'.format(cls))
            except:
                raise ImproperlyConfigured()


    def unregister_segment_plugin(self, plugin_instance):
        '''
        Removes the given plugin from the SegmentPool.
        '''

        #
        # NOTE: In many cases, the configuration of a given plugin may have
        # changed before we receive the call to unregister it. So, we'll look
        # for the plugin in all CFGS for this plugin's class.
        #

        if not isinstance(plugin_instance, SegmentBasePluginModel):
            raise ImproperlyConfigured('Segment Plugins must subclasses of '
                'SegmentBasePluginModel. {0} is not.'.format(
                    plugin_instance.get_plugin_class_instance().__class__.__name__
                ))
        else:
            plugin_class_instance = plugin_instance.get_plugin_class_instance()
            if plugin_class_instance.allow_overrides:
                #
                # A segment plugin that doesn't allow overrides wouldn't be
                # registered in the first place.
                #
                plugin_class_name = plugin_class_instance.__class__.__name__

                if plugin_class_name in self.segments:
                    segment_class = self.segments[plugin_class_name]
                    segment_configs = segment_class[self.CFGS]
                    for configuration, data in segment_configs.items():
                        if plugin_instance in data[self.INSTANCES]:
                            # Found it! Now remove it...
                            data[self.INSTANCES].remove(plugin_instance)
                            self._sorted_segments = dict()

                            # Clean-up any empty elements caused by this removal...
                            if len(data[self.INSTANCES]) == 0:
                                # OK, this was the last one, so...
                                del segment_configs[configuration]

                                if len(segment_configs) == 0:
                                    # This too was the last one
                                    del self.segments[plugin_class_name]
            return

        try:
            cls = plugin_instance.get_plugin_class_instance().__class__.__name__
            raise PluginNotRegistered('The segment plugin {0} cannot be '
                'unregistered because it is not currently registered in the '
                'SegmentPool.'.format(cls))
        except:
            raise PluginNotRegistered()


    def set_override(self, user, segment_class, segment_config, override):
        '''
        (Re-)Set an override on a segment (segment_class x segment_config).
        '''

        overrides = self.segments[segment_class][self.CFGS][segment_config][self.OVERRIDES]
        if override == SegmentOverride.NoOverride:
            del overrides[user.username]
        else:
            overrides[user.username] = override
        self._sorted_segments = dict()


    def reset_all_segment_overrides(self, user):
        '''
        Resets (disables) the overrides for all segments.
        '''

        for segment_class in self.segments.values():
            for configuration in segment_class[self.CFGS].values():
                for username, override in configuration[self.OVERRIDES].items():
                    if username == user.username:
                        configuration[self.OVERRIDES][username] = SegmentOverride.NoOverride
        self._sorted_segments = dict()


    def get_num_overrides_for_user(self, user):
        '''
        Returns a count of the number of overrides for all segments for the
        given user. This is used for the toolbar menu where we show the number
        of active overrides.
        '''

        num = 0
        for segment_class_name, segment_class in self.segments.items():
            for config_str, config in segment_class[self.CFGS].items():
                for username, override in config[self.OVERRIDES].items():
                    if username == user.username and int(override):
                        num += 1
        return num


    def get_override_for_classname(self, user, plugin_class_name, segment_config):
        '''
        Given the user, plugin_class_name and segment_config, return the
        current override, if any.
        '''

        #
        # Note: segment_config can be either of:
        #
        # 1. A number string of text
        # 2. A lazy translation object (Promise)
        #

        lang = get_language()
        activate('en')
        if isinstance(segment_config, Promise):
            segment_key = force_text(segment_config)
        elif isinstance(segment_config, six.text_type):
            segment_key = segment_config
        else:
            segment_key = segment_config
        activate(lang)

        try:
            overrides = self.segments[plugin_class_name][self.CFGS][segment_key][self.OVERRIDES]

            if user.username in overrides:
                #  TODO: I don't like this int-casting used here or anywhere.
                return int(overrides[user.username])

        except KeyError:
            if not isinstance(segment_config, Promise):
                import inspect
                warnings.warn('get_override_for_segment() received '
                    'segment_config: “{0}” as type {1} from: {2!r}. '
                    'This has resulted in a failure to retrieve a '
                    'segment override.'.format(
                        segment_config,
                        type(segment_config),
                        inspect.stack()[1][3]
                    )
                )

        return SegmentOverride.NoOverride


    def get_override_for_segment(self, user, plugin_class_instance, plugin_instance):
        '''
        Given a specific user, plugin class and instance, return the current
        override. This is a wrapper around get_override_for_classname() and
        provides the appropriate duck-checking and is therefore more useful as
        an external entry-point into the segment_pool.
        '''

        if (hasattr(plugin_class_instance, 'allow_overrides') and
                plugin_class_instance.allow_overrides and
                hasattr(plugin_instance, 'configuration_string')):

            segment_class = plugin_class_instance.__class__.__name__
            segment_config = plugin_instance.configuration_string

            return self.get_override_for_classname(user, segment_class, segment_config)

        return SegmentOverride.NoOverride


    def _get_sorted_copy(self):
        '''
        Returns the SegmentPool as a list of tuples sorted appropriately for
        human consumption in *the current language*. This means that the
        _(NAME) value should determine the sort order of the outer dict and
        the _('segment_config') key should determine the order of the inner
        dicts. In both cases, the keys need to be compared in the provided
        language.

        Further note that the current language is given by get_language() and
        that this will reflect the CMS operator's user settings, NOT the current
        PAGE language.

        NOTE: that the structure of the sorted pool is different. Two of the
        nested dicts are now lists of tuples so that the sort can be retained.

        _sorted_segments = [
            (/class/, {
                NAME: _(/name/),
                CFGS: [
                    (/configuration_string/, {
                        LABEL: _(/configuration_string/),
                        OVERRIDES: {
                            /user.id/: /SegmentOverride enum value/,
                            ...
                        },
                        INSTANCES: [ ... ]
                    })
                ]
            })
        ]

        NOTE: On Python 3.0+ systems, we depend on pyuca for collation, which
        produces excellent results. On earlier systems, this is not available,
        so, we use a cruder mapping of accented characters into their
        unaccented ASCII equivalents.
        '''

        sort_key = None
        if sys.version_info >= (3, 0):
            uca = None
            #
            # Unfortunately, the pyuca class–which can provide collation of
            # strings in a thread-safe manner–is for Python 3.0+ only
            #
            try:
                from pyuca import Collator
                uca = Collator()
                sort_key = uca.sort_key
            except:
                pass                

        if not sort_key:
            #
            # Our fallback position is to use a more simple approach of
            # mapping 'accented' chars to latin equivalents before sorting,
            # this is crude, but better than nothing.
            #
            from .unaccent import unaccented_map

            def sort_key(s):
                return s.translate(unaccented_map())

        pool = self.segments
        clone = []
        for cls_key in sorted(pool.keys()):
            cls_dict = {
                self.NAME: pool[cls_key][self.NAME],
                self.CFGS: list(),
            }
            clone.append(( cls_key, cls_dict ))
            # We'll build the CFG as a list in arbitrary order for now...
            for cfg_key in pool[cls_key][self.CFGS]:
                cfg_dict = {
                    self.LABEL: pool[cls_key][self.CFGS][cfg_key][self.LABEL],
                    self.OVERRIDES: dict(),
                    self.INSTANCES: list(),
                }
                for username, override in pool[cls_key][self.CFGS][cfg_key][self.OVERRIDES].items():
                    cfg_dict[self.OVERRIDES][username] = override
                for instance in pool[cls_key][self.CFGS][cfg_key][self.INSTANCES]:
                    cfg_dict[self.INSTANCES].append(instance)
                cls_dict[self.CFGS].append( (cfg_key, cfg_dict) )
            #
            # Now, sort the CFGS by their LABEL, using which every means we
            # have available to us at this moment.
            #
            cls_dict[self.CFGS] = sorted(cls_dict[self.CFGS], key=lambda x: sort_key(force_text(x[1][self.LABEL])))

        return clone


    def get_registered_segments(self):
        lang = get_language()
        if not lang in self._sorted_segments:
            self._sorted_segments[lang] = self._get_sorted_copy()

        return self._sorted_segments[lang]


    def get_segments_toolbar_menu(self, user, toolbar, csrf_token):
        '''
        Returns a CMSToolbar "Segments" menu from the pool.
        '''

        pool = self.get_registered_segments()

        num_overrides = self.get_num_overrides_for_user(user)

        if num_overrides:
            segment_menu_name = _('Segments ({num:d})'.format(num=num_overrides))
        else:
            segment_menu_name = _('Segments')

        segment_menu = toolbar.get_or_create_menu(
            'segmentation-menu',
            segment_menu_name
        )

        for segment_class_name, segment_class in pool:
            segment_name = segment_class[self.NAME]

            segment_class_menu = segment_menu.get_or_create_menu(
                segment_class_name,
                segment_name
            )

            for config_str, config in segment_class[self.CFGS]:

                user_override = segment_pool.get_override_for_classname(
                    user,
                    segment_class_name,
                    config_str
                )

                config_menu = SubMenu(config[self.LABEL], csrf_token)
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
            # TODO: This should not use a named pattern
            action=reverse('admin:reset_all_segment_overrides'),
            csrf_token=csrf_token,
            data={},
            disabled=bool(num_overrides == 0),
            on_success=toolbar.REFRESH_PAGE
        )
        segment_menu.add_item(reset_ajax_item)


    def __str__(self):
        '''
        Returns the whole segment_pool structure. Useful for debugging. Not
        much else.
        '''

        return self.segments


segment_pool = SegmentPool()
