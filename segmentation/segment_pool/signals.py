# -*- coding: utf-8 -*-

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ImproperlyConfigured

from cms.exceptions import PluginAlreadyRegistered, PluginNotRegistered
from .segment_pool import segment_pool


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
        except (PluginAlreadyRegistered, ImproperlyConfigured):
            pass

    # Either way, we register it.
    try:
        segment_pool.register_segment_plugin(instance)
    except (PluginAlreadyRegistered, ImproperlyConfigured):
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
