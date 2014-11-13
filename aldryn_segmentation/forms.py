# -*- coding: utf-8 -*-

from django.forms import CharField, ChoiceField, HiddenInput
from django.forms.models import ModelForm
from django.utils.translation import ugettext as _

from .segment_pool import segment_pool
from cms.models import CMSPlugin


class SetCookieAdminForm(ModelForm):

    class Meta:
        fields = [
            'key', 'value', 'setting', 'path_choice',
            'days_to_expire', 'overwrite', 'original_referer',
        ]

    #
    # This presents the existing Cookie Segment configurations for selection.
    #
    setting = ChoiceField(
        label=_(u'Segment'),
        help_text=_(u'Or, choose an existing Cookie Segment to copy the key/value pair from.'),
        required=False,
    )

    #
    # This will store the original original_referer, used for deterimining the
    # correct path_choices.
    #
    original_referer = CharField(
        widget=HiddenInput,
    )

    #
    # This presents choices for selecting an appropriate cookie path
    #
    path_choice = ChoiceField(
        label=_(u'Path'),
        help_text=_(u'Choose the scope of this cookie.'),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        """
        Set up the choices and initial values for the non-model-based widgets.
        """

        #
        # Note: `request` doesn't exist in kwargs unless we add if via the
        # superclassing hack in SetCookiePlugin.get_form().
        #
        self.request = kwargs.pop('request', None)
        super(SetCookieAdminForm, self).__init__(*args, **kwargs)

        #
        # We do NOT want the new referer after a for submission, we only want
        # the original one. If this form is bound, we'll grab the
        # original_referer from that.
        #

        if 'instance' in kwargs:
            self.instance = kwargs['instance']

        if self.is_bound:
            original_referer = self.data.get('original_referer')
        else:
            if self.request:
                original_referer = self.request.META['HTTP_REFERER']
                self.fields['original_referer'].initial = original_referer

        choices = [('/', '/', )]
        if original_referer:
            if '://' in original_referer:
                loc = original_referer.find('://')
                original_referer = original_referer[loc + 3:]
            segments = original_referer[original_referer.find('/'):].split('/')
            for s in range(2,len(segments)):
                path = '/'.join(segments[0:s])
                choices.append((path, path, ))
        self.fields['path_choice'].choices = choices

        if self.instance:
            self.fields['path_choice'].initial = self.instance.path

        #
        # Here we extract a list of the configuration strings for all the
        # CookieSegmentPlugin's, then we just grab the first instance of one
        # of them to store as the 'value' of each choice. This will be used in
        # the save() method below to extract the cookie_key and cookie_value
        # from the relevant CookieSegmentPlugin for setting this plugin's key
        # and value fields.
        #
        choices = [(0, '--------', ), ]
        pool = segment_pool.get_registered_segments()
        for segment_class_name, segment_class in pool:
            if segment_class_name == 'CookieSegmentPlugin':
                for config_str, config in segment_class['CFGS']:
                    instance = config['INSTANCES'][0]
                    choices.append((instance.id, config['LABEL'], ))

        self.fields['setting'].choices = choices


    def save(self, force_insert=False, force_update=False, commit=True):
        '''
        Save the selected setting and path, if any, into the plugin's fields
        properly.
        '''
        # Saves the form
        plugin = super(SetCookieAdminForm, self).save(commit=False)

        setting = self.cleaned_data['setting']
        if setting:
            try:
                segment_plugin = CMSPlugin.objects.get(id=setting)
            except CMSPlugin.DoesNotExist:
                segment_plugin = None
                pass

            if segment_plugin:
                segment_inst, segment_klass = segment_plugin.get_plugin_instance()
                plugin.key = segment_inst.cookie_key
                plugin.value = segment_inst.cookie_value

        plugin.path = self.cleaned_data['path_choice']

        plugin.save()
        return plugin
