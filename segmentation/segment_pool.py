# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from cms.exceptions import PluginAlreadyRegistered, PluginNotRegistered
from cms.plugin_pool import plugin_pool

from sortedcontainers import SortedDict

from .cms_plugins import SegmentPluginBase
from .models import SegmentBasePluginModel


#
# A simple enum for Python's < 3.4.
#
class SegmentOverride:
    NoOverride, ForcedActive, ForcedInactive = range(3)


class SegmentPool(object):
    '''
    This maintains a sorted dict of sorted dict of list of segment plugin
    instances in the form:

    segments = {
        /class/ : {
            'name': /name/,
            'configurations': {
                /configuration_string/ : {
                    'override': /SegmentOverride enum value/,
                    'instances': [ ... ]
                }
            }
        }
    }
    '''
    def __init__(self):
        self.segments = SortedDict()
        self._sorted_segments = None
        self.discover()


    def discover(self):
        '''
        Find and register any SegmentPlugins already configured...
        '''

        for plugin_class in plugin_pool.get_all_plugins():
            if issubclass(plugin_class, SegmentPluginBase) and plugin_class.allow_overrides:
                for plugin_instance in plugin_class.model.objects.all():
                    self.register_segment_plugin(plugin_instance)

    def register_segment_plugin(self, plugin_instance):
        '''
        Registers the provided plugin_instance into the SegmentPool.
        '''
        plugin_class_instance = plugin_instance.get_plugin_class_instance()
        if isinstance(plugin_class_instance, SegmentPluginBase):

            plugin_class_name = plugin_class_instance.__class__.__name__
            plugin_name = plugin_class_instance.name

            if plugin_class_name not in self.segments:

                #
                # NOTE: We're using a sortedcontainers.SortedDict here for the
                # configurations dict. This shifts the burden of sorting to
                # add/remove operations rather than when it is read, which is
                # appropriate for this implementation.
                #
                # We do not use a SortedDict for the outer-most dict because
                # we'll be sorting that on one of the values (name), rather
                # than the keys. Plus, this should be much faster to sort
                # anyway.
                #
                self.segments.update({
                    plugin_class_name: {
                        'name': plugin_name,    
                        'configurations': SortedDict(),
                    }
                })
                self._sorted_segments = None
            segment_class = self.segments[plugin_class_name]

            plugin_config = plugin_instance.configuration_string
            segment_configs = segment_class['configurations']

            if plugin_config not in segment_configs:
                segment_configs.update( { plugin_config: dict() } )
                self._sorted_segments = None
            segment_config = segment_configs[plugin_config]

            if len(segment_config) == 0:
                segment_config['override'] = SegmentOverride.NoOverride
                segment_config['instances'] = list()
                self._sorted_segments = None

            if plugin_instance not in segment_config['instances']:
                segment_config['instances'].append( plugin_instance )
                self._sorted_segments = None
            else:
                raise PluginAlreadyRegistered('The segment plugin (%r) cannot be registered because it already is.' % plugin_instance)
        else:
            raise ImproperlyConfigured('Segment Plugins must subclasses of SegmentPluginBase. %r is not.' % plugin_class_instance)


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
            raise ImproperlyConfigured('Segment Plugins must subclasses of SegmentPluginBase. %r is not.' % plugin_class_instance)
        else:
            plugin_class_name = plugin_class_instance.__class__.__name__

            if plugin_class_name in self.segments:
                segment_class = self.segments[plugin_class_name]
                segment_configs = segment_class['configurations']
                for configuration, data in segment_configs.iteritems():
                    if plugin_instance in data['instances']:
                        # Found it! Now remove it...
                        data['instances'].remove(plugin_instance)
                        self._sorted_segments = None

                        # Clean-up any empty elements caused by this removal...
                        if len(data['instances']) == 0:
                            # OK, this was the last one, so...
                            del segment_configs[configuration]

                            if len(segment_configs) == 0:
                                # This too was the last one
                                self.segments.remove(plugin_class_name)

                        return
        raise PluginNotRegistered('The segment plugin (%r) cannot be unregistered because it is not currently registered in the SegmentPool. (#1)' % plugin_instance)


    def get_registered_segments(self):
        '''
        Returns the SegmentPool sorted appropriately for human consumption.
        '''

        #
        # NOTE: Due to our use of sortedcontainers.SortedDict(), the
        # 'configurations' sub-struct is already sorted alphabetically which
        # is useful for proper presentation in menus.
        #
        # The outermost dict is also a SortedDict, because we need it to
        # retain a sort, but not necessarily an automatic one. We need it to
        # be sorted by the 'name' item within, not the key itself. This is
        # easy and quick to do with Python, but, we don't need/want to do this
        # unless necessary, since this will be called for every request during
        # an operator's session.
        #
        if not self._sorted_segments:
            self._sorted_segments = self.segments
            # TODO: How to sort this properly!

        return self._sorted_segments


    def set_override(self, segment_class, segment_config, override, value=True):
        '''
        (Re-)Set an override on a segment (segment_class x segment_config).
        '''

        if value:
            self.segments[segment_class]['configurations'][segment_config]['override'] = override
        else:
            self.segments[segment_class]['configurations'][segment_config]['override'] = SegmentOverride.NoOverride


    def reset_all_segment_overrides(self):
        '''
        Resets (disables) the overrides for all segments.
        '''
        for segment_class in self.segments.itervalues():
            for configuration in segment_class['configurations'].itervalues():
                configuration['override'] = SegmentOverride.NoOverride

    def get_override_for_segment(self, segment_class, segment_config):
        '''
        Given a specific segment/configuration, return the current override.
        '''

        return int(self.segments[segment_class]['configurations'][segment_config]['override'])


segment_pool = SegmentPool()


@receiver(post_save)
def register_segment(sender, instance, created, **kwargs):
    '''
    Ensure that saving changes in the model results in the de- registering (if
    necessary) and registering of this segment plugin.
    '''

    from .segment_pool import segment_pool

    if isinstance(instance, SegmentBasePluginModel):
        allow_overrides = instance.get_plugin_class_instance().allow_overrides

        # If this isn't a new plugin, then we need to unregister first.
        if not created and allow_overrides:
            try:
                segment_pool.unregister_segment_plugin(instance)
            except PluginNotRegistered:
                pass

        # Either way, we register it.
        if allow_overrides:
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
