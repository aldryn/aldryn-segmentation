# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from cms.utils.compat.dj import force_unicode

from .segment_pool import segment_pool


@require_POST
def set_segment_override(request):
    '''
    This view (re)sets an override on a specific segment.
    '''

    segment_class = request.POST.get('segment_class', None)
    segment_config = request.POST.get('segment_config', None)
    override = request.POST.get('override', None)
    value = request.POST.get('value', None)

    if value in ['True', 'true', '1', 'yes']:
        value = True
    else:
        value = False

    segment_pool.set_override(segment_class, segment_config, override, value)
    return HttpResponse(force_unicode(_("The segment override was successfully changed.")))


def reset_all_segment_overrides(request):
    '''
    This view resets all segment overrides in one go.
    '''

    segment_pool.reset_all_segment_overrides()
    return HttpResponse(force_unicode(_("The all segment override were successfully reset.")))
