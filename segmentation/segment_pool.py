# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import six
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.functional import Promise
from django.utils.translation import activate, get_language, ugettext_lazy as _

from cms.exceptions import PluginAlreadyRegistered, PluginNotRegistered
from cms.plugin_pool import plugin_pool
from cms.toolbar.items import SubMenu, Break, AjaxItem

from .cms_plugins import SegmentPluginBase
from .models import SegmentBasePluginModel

import logging
logger = logging.getLogger(__name__)


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

    NOTE: The key for a given configuration is the configuration string realised
    as 'en' unicode. The unresolved gettext proxy of the same is stored under
    the key LABEL.

    Although this is implmented as a non-persistent, system-wide singleton, it
    is shared by all operators of the system. In order to keep them from
    setting overrides against each other, we need to be able to store per-
    operator overrides. We do this by keying the overrides with the user id of
    the operator who created it.
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


        #
        # TODO: Consider looking for ducks instead of instances.
        #
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
                    logger.warn('register_segment: Not really sure what '
                                'configuration_string returned!')

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
                    raise PluginAlreadyRegistered('The segment plugin (%r) cannot '
                        'be registered because it already is.' % plugin_instance)

        else:
            raise ImproperlyConfigured('Segment Plugins must subclasses of '
                'SegmentBasePluginModel. %r is not.' % plugin_instance)


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
                'SegmentBasePluginModel. %r is not.' % plugin_instance)
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
                    for configuration, data in segment_configs.iteritems():
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

        raise PluginNotRegistered('The segment plugin (%r) cannot be '
            'unregistered because it is not currently registered in the '
            'SegmentPool. (#1)' % plugin_instance)


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

        for segment_class in self.segments.itervalues():
            for configuration in segment_class[self.CFGS].itervalues():
                for username, override in configuration[self.OVERRIDES].iteritems():
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
        for segment_class_name, segment_class in self.segments.iteritems():
            for config_str, config in segment_class[self.CFGS].iteritems():
                for username, override in config[self.OVERRIDES].iteritems():
                    if username == user.username and int(override):
                        num += 1
        return num


    def get_override_for_segment(self, user, plugin_class_instance, plugin_instance):
        '''
        Given a specific segment/configuration, return the current override.
        '''

        if (hasattr(plugin_class_instance, 'allow_overrides') and
                plugin_class_instance.allow_overrides and
                hasattr(plugin_instance, 'configuration_string')):

            segment_class = plugin_class_instance.__class__.__name__
            segment_config = plugin_instance.configuration_string

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
                overrides = self.segments[segment_class][self.CFGS][segment_key][self.OVERRIDES]

                if user.username in overrides:
                    #  TODO: I don't like this int-casting used here or anywhere.
                    return int(overrides[user.username])

            except KeyError:
                if not isinstance(segment_config, Promise):
                    import inspect
                    # TODO: This should be stronger than a log. (warning or exception?)
                    logger.error(u'get_override_for_segment received '
                        'segment_config: “%s” as type %s from: %s. This has '
                        'resulted in a failure to retrieve a segment override.' % (
                            segment_config,
                            type(segment_config),
                            inspect.stack()[1][3])
                    )

        #
        # Either, this doesn't quack right, or, this plugin just wasn't found,
        # or it just doesn't have an override for this user. So, there's no
        # override.
        #
        return SegmentOverride.NoOverride


    def get_registered_segments(self):
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
        '''

        from copy import deepcopy

        lang = get_language()
        if not lang in self._sorted_segments:
            #
            # Sort the outer dict in the current language, convering it to a
            # list of tuples. Note, we're taking starting from a deep copy of
            # the original pool dict to prevent affecting it.
            #
            self._sorted_segments[lang] = sorted(
                deepcopy(self.segments).items(),
                key=lambda x: x[1][self.NAME].encode('utf-8')
            )

            #
            # Sort each of the inner dicts in the current language, converting
            # them to lists of tuples too.
            #
            for _, segment_class in self._sorted_segments[lang]:
                segment_class[self.CFGS] = sorted(
                    segment_class[self.CFGS].items(),
                    key=lambda x: force_text(x[1][self.LABEL])
                )

        return self._sorted_segments[lang]


    def get_segments_toolbar_menu(self, user, toolbar, csrf_token):
        '''
        Returns a CMSToolbar "Segments" menu from the pool.
        '''

        pool = self.get_registered_segments()

        num_overrides = self.get_num_overrides_for_user(user)

        segment_menu_name = _('Segments (%s)' % num_overrides) if num_overrides else _('Segments')
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

                user_override = segment_pool.get_override_for_segment(
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
            action=reverse('admin:reset_all_segment_overrides'),
            csrf_token=csrf_token,
            data={},
            disabled=bool(num_overrides == 0),
            on_success=toolbar.REFRESH_PAGE
        )
        segment_menu.add_item(reset_ajax_item)


    def __str__(self):
        # Punt!
        return self.segments


segment_pool = SegmentPool()


@receiver(post_save)
def register_segment(sender, instance, created, **kwargs):
    '''
    Ensure that saving changes in the model results in the de-registering (if
    necessary) and registering of this segment plugin.
    '''

    #
    # NOTE: Removed the test if instance is the right type from here, as it is
    # already the first thing that happens in the (un)register_plugin()
    # methods. Its not these signal handlers' job to decide who gets to be
    # registered and who doesn't.
    #

    if not created:
        try:
            segment_pool.unregister_segment_plugin(instance)
        except (PluginNotRegistered, ImproperlyConfigured):
            pass

    # Either way, we register it.
    try:
        segment_pool.register_segment_plugin(instance)
    except (PluginNotRegistered, ImproperlyConfigured):
        pass


@receiver(pre_delete)
def unregister_segment(sender, instance, **kwargs):
    '''
    Listens for signals that a SegmentPlugin instance is to be deleted, and
    un-registers it from the segment_pool.
    '''

    # NOTE: See note in register_segment()

    try:
        segment_pool.unregister_segment_plugin(instance)
    except (PluginNotRegistered, ImproperlyConfigured):
        pass
