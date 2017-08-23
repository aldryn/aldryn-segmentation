# -*- coding: utf-8 -*-
from aldryn_client import forms


class Form(forms.BaseForm):

    def to_settings(self, data, settings):
        settings['INSTALLED_APPS'].extend([
            'aldryn_segmentation',
        ])
        return settings
