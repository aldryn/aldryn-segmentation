# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.utils.translation import get_language, ugettext, ugettext_lazy as _
from cms.exceptions import PluginAlreadyRegistered, PluginNotRegistered
from cms.plugin_pool import plugin_pool

from .cms_plugins import SegmentPluginBase
from .models import SegmentBasePluginModel

import logging
logger = logging.getLogger(__name__)

#
# A simple enum for Python's < 3.4.
#
class SegmentOverride:
    NoOverride, ForcedActive, ForcedInactive = range(3)

    overrides_list = [
        (NoOverride, _('No override')),
        (ForcedActive, _('Forced active')),
        (ForcedInactive, _('Forced inactive')),
    ]



class SegmentPool(object):
    '''
    This maintains a set of nested sorted dicts containing, among other
    attributes, a list of segment plugin instances in the form:

    segments = {
        /class/ : {
            'NAME': _(/name/),
            'CONFIGURATIONS': {
                _(/configuration_string/) : {
                    'OVERRIDES': {
                        /user.id/: /SegmentOverride enum value/,
                        ...
                    },
                    'INSTANCES': [ ... ]
                }
            }
        }
    }

    Although this is implmented as a non-persistent, system-wide singleton, it
    is shared by all operators of the system. In order to keep them from
    setting overrides against each other, we need to be able to store per-
    operator overrides. We do this by keying the overrides with the user id of
    the operator who created it.
    '''

    def __init__(self):
        self.segments = dict()
        # TODO: wrap this shadow dict of dicts into an abstraction layer?
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
        '''

        plugin_class_instance = plugin_instance.get_plugin_class_instance()

        #
        # TODO: Consider looking for ducks instead of instances.
        #
        if isinstance(plugin_class_instance, SegmentPluginBase):
            plugin_class_name = plugin_class_instance.__class__.__name__
            plugin_name = plugin_class_instance.name

            if plugin_class_name not in self.segments:
                self.segments[plugin_class_name] = {
                    'NAME': plugin_name,    
                    'CONFIGURATIONS': dict(),
                }
                self._sorted_segments = dict()
            segment_class = self.segments[plugin_class_name]

            plugin_config = plugin_instance.configuration_string
            segment_configs = segment_class['CONFIGURATIONS']

            if plugin_config not in segment_configs:
                segment_configs[plugin_config] =  dict()
                self._sorted_segments = dict()
            segment = segment_configs[plugin_config]

            if len(segment) == 0:
                segment['OVERRIDES'] = dict()
                segment['INSTANCES'] = list()
                self._sorted_segments = dict()

            if plugin_instance not in segment['INSTANCES']:
                segment['INSTANCES'].append( plugin_instance )
                self._sorted_segments = dict()
            else:
                raise PluginAlreadyRegistered('The segment plugin (%r) cannot '
                    'be registered because it already is.' % plugin_instance)
        else:
            raise ImproperlyConfigured('Segment Plugins must subclasses of '
                'SegmentPluginBase. %r is not.' % plugin_class_instance)


    def unregister_segment_plugin(self, plugin_instance):
        '''
        Removes the given plugin from the SegmentPool.
        '''

        #
        # NOTE: In many cases, the configuration of a given plugin may have
        # changed before we receive the call to unregister it. So, we'll look
        # for the plugin in all 'configurations' for this plugin's class.
        #

        plugin_class_instance = plugin_instance.get_plugin_class_instance()
        
        if not isinstance(plugin_class_instance, SegmentPluginBase):
            raise ImproperlyConfigured('Segment Plugins must subclasses of '
                'SegmentPluginBase. %r is not.' % plugin_class_instance)
        else:
            plugin_class_name = plugin_class_instance.__class__.__name__

            if plugin_class_name in self.segments:
                segment_class = self.segments[plugin_class_name]
                segment_configs = segment_class['CONFIGURATIONS']
                for configuration, data in segment_configs.iteritems():
                    if plugin_instance in data['INSTANCES']:
                        # Found it! Now remove it...
                        data['INSTANCES'].remove(plugin_instance)
                        self._sorted_segments = dict()

                        # Clean-up any empty elements caused by this removal...
                        if len(data['INSTANCES']) == 0:
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

        overrides = self.segments[segment_class]['CONFIGURATIONS'][segment_config]['OVERRIDES']
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
            for configuration in segment_class['CONFIGURATIONS'].itervalues():
                for username, override in configuration['OVERRIDES'].iteritems():
                    if username == user.username:
                        configuration['OVERRIDES'][username] = SegmentOverride.NoOverride
        self._sorted_segments = dict()


    def get_num_overrides_for_user(self, user):
        '''
        Returns a count of the number of overrides for all segments for the
        given user. This is used for the toolbar menu where we show the number
        of active overrides.
        '''

        num = 0
        for segment_class_name, segment_class in self.segments.iteritems():
            for config_str, config in segment_class['CONFIGURATIONS'].iteritems():
                for username, override in config['OVERRIDES'].iteritems():
                    if username == user.username and override > 0:
                        num += 1
        return num


    #
    # TODO: I don't like this int-casting used here or anywhere.
    #
    def get_override_for_segment(self, user, segment_class, segment_config):
        '''
        Given a specific segment/configuration, return the current override.
        '''
        overrides = self.segments[segment_class]['CONFIGURATIONS'][segment_config]['OVERRIDES']

        if user.username in overrides:
            return int(overrides[user.username])
        else:
            return SegmentOverride.NoOverride


    def get_registered_segments(self):
        '''
        Returns the SegmentPool as a list of tuples sorted appropriately for
        human consumption in *the current language*. This means that the
        _('name') value should determine the sort order of the outer dict and
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
                'NAME': _(/name/),
                'CONFIGURATIONS': [
                    (_(/configuration_string/), {
                        'OVERRIDES': {
                            /user.id/: /SegmentOverride enum value/,
                            ...
                        },
                        'INSTANCES': [ ... ]
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
                key=lambda x: x[1]['NAME'].encode('utf-8')
            )

            #
            # Sort each of the inner dicts in the current language, converting
            # them to lists of tuples too.
            #
            for _, segment_class in self._sorted_segments[lang]:
                segment_class['CONFIGURATIONS'] = sorted(
                    segment_class['CONFIGURATIONS'].items(),
                    key=lambda x: ugettext(x[0]).encode('utf-8')
                )

        return self._sorted_segments[lang]


segment_pool = SegmentPool()


@receiver(post_save)
def register_segment(sender, instance, created, **kwargs):
    '''
    Ensure that saving changes in the model results in the de- registering (if
    necessary) and registering of this segment plugin.
    '''

    from .segment_pool import segment_pool

    #
    # TODO: Should we be looking for ducks?
    #
    if isinstance(instance, SegmentBasePluginModel) and instance.get_plugin_class_instance().allow_overrides:
        # If this isn't a new plugin, then we need to unregister first.
        if not created:
            try:
                segment_pool.unregister_segment_plugin(instance)
            except PluginNotRegistered:
                pass

        # Either way, we register it.
        try:
            segment_pool.register_segment_plugin(instance)
        except PluginAlreadyRegistered:
            pass


@receiver(pre_delete)
def unregister_segment(sender, instance, **kwargs):
    '''
    Listens for signals that this SegmentPlugin instance is to be deleted, and
    un-registers it from the segment_pool.
    '''

    from .segment_pool import segment_pool

    if isinstance(instance, SegmentBasePluginModel):
        plugin_class = instance.get_plugin_class_instance()

        if plugin_class.allow_overrides:
            try:
                segment_pool.unregister_segment_plugin(instance)
            except PluginNotRegistered:
                pass
