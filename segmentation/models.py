# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import types

from django.db import models
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, string_concat

from cms.models import CMSPlugin


#
# NOTE: The SegmentLimitPluginModel does NOT subclass SegmentBasePluginModel
#
@python_2_unicode_compatible
class SegmentLimitPluginModel(CMSPlugin):

    #
    # Need to consider how best to display this in the Plugin Change Form...
    #
    #   0 means "Display ALL segments that match",
    #   1 means "Display first matching segment",
    #   2 means "Display up to two matching segments,"
    #     and so on...
    #

    label = models.CharField(_('label'),
        blank=True,
        default='',
        help_text=_('Optionally set a label for this limit block.'),
        max_length=128,
    )

    max_children = models.PositiveIntegerField(_('# of matches to display'),
        blank=False,
        default=1,
        help_text=_('Display up to how many matching segments?'),
    )

    @property
    def configuration_string(self):
        if self.max_children == 0:
            return _('Show All')
        elif self.max_children == 1:
            return _('Show First')
        else:
            return string_concat(_('Show First'), ' ', self.max_children)


    def __str__(self):
        '''
        If there is a label, show that with the configuration in brackets,
        otherwise, just return the configuration string.
        '''

        if self.label:
            conf_str = _('%(label)s [%(config)s]') % {
                'label': self.label,
                'config': self.configuration_string,
            }
        else:
            conf_str = self.configuration_string

        return force_text(conf_str)


@python_2_unicode_compatible
class SegmentBasePluginModel(CMSPlugin):
    
    #
    # Defines a common interface for segment plugins. Also note that plugin
    # model's subclassing this class will automatically be (un-)registered
    # (from)to the segment_pool via 'pre_delete' and 'post_save' signals. This
    # is implemented in segmentation.segment_pool.
    #

    class Meta:
        abstract = True

    label = models.CharField(_('label'),
        blank=True,
        default='',
        max_length=128,
    )


    @property
    def configuration_string(self):
        '''
        Return a ugettext_lazy object (or a lazy function that returns the
        same) that represents the configuration for the plugin instance in a
        unique, concise manner that is suitable for a toolbar menu option.

        Some Examples:
            Cookie:
                '"key" equals "value"'
            Country:
                'Country is Kenya'
            Auth:
                'User is authenticated'
            Switch:
                'Always ON'
            Limit:
                'Show First'

        In cases where the returned string is composed with placeholders, E.g.:

            Cookie:
                ugettext_lazy('“{key}” equals “{value}”').format(
                    key=self.key,
                    value=self.value
                )

        You *must* actually return a evaluated, lazy wrapper around the
        gettext_lazy operation as follows:

            def configuration_string(self):
                wrapper():
                    return ugettext_lazy('“{key}” equals “{value}”').format(
                        key=self.key,
                        value=self.value
                    )

                # NOTE: the trailing '()'
                return lazy(wrapper, six.text_type)()

        Otherwise, the translations won't happen.

        This construction is not required for untranslated or non-
        parameterized translations.


        NOTE: Each subclass must override to suit.
        '''
        raise NotImplementedError("Please Implement this method")


    def __str__(self):
        '''
        If there is a label, show that with the configuration in brackets,
        otherwise, just return the configuration string.
        '''

        conf = self.configuration_string

        # TODO: This should no longer be necessary.
        if isinstance(conf, types.FunctionType):
            conf_str = conf()
        else:
            conf_str = conf

        if self.label:
            return _('%(label)s [%(config)s]') % {
                'label': self.label,
                'config': conf_str,
            }
        else:
            return force_text(conf_str)


class FallbackSegmentPluginModel(SegmentBasePluginModel):

    @property
    def configuration_string(self):
        return _('Always active')


class SwitchSegmentPluginModel(SegmentBasePluginModel):

    on_off = models.BooleanField(_('Always on?'),
        default=True,
        help_text=_('Uncheck to always hide child plugins.'),
    )

    @property
    def configuration_string(self):
        if self.on_off:
            return _('Always ON')
        else:
            return _('Always OFF')


class CookieSegmentPluginModel(SegmentBasePluginModel):

    #
    # Consider that we should probably support either:
    #   Simple wildcard '*', '?' expressions or
    #   RegEx expressions or
    #   Both.
    #
    # A note about the max_lengths selected: browsers can support up to 4093
    # characters for a given cookie (combining both the key and the value). So
    # either one can be up to 4092 chars in length. Since these are
    # implemented as VarChars, this shouldn't be too wasteful and still
    # support almost anything.
    #
    # NOTE: This forces a requirement for MySQL users to be using 5.0.3 or
    # later (which is already a requirement for Django 1.5+).
    #

    cookie_key = models.CharField(_('name of cookie'),
        blank=False,
        default='',
        help_text=_('Name of cookie to consider.'),
        max_length=4096,
    )

    cookie_value = models.CharField(_('value to compare'),
        blank=False,
        default='',
        help_text=_('Value to consider.'),
        max_length=4096,
    )

    @property
    def configuration_string(self):

        def wrapper():
            return _('“{key}” equals “{value}”').format(key=self.cookie_key, value=self.cookie_value)

        return lazy(
            wrapper,
            six.text_type
        )()


class CountrySegmentPluginModel(SegmentBasePluginModel):

    #
    # NOTE: This list is derived from MaxMind's datasets
    # (http://dev.maxmind.com/geoip/legacy/codes/iso3166/), so contains non-
    # country entities such as "A1", "A2", "O1" as well pseudo-countries such as
    # "EU", "AP" etc. These are very relevant to this implementation.
    #
    # MaxMind also state: “Please note that "EU" and "AP" codes are only used
    # when a specific country code has not been designated (see FAQ). Blocking
    # or re-directing by "EU" or "AP" will only affect a small portion of IP
    # addresses. Instead, you should list the countries you want to block/re-
    # direct individually.”
    #
    # TODO: Move this and related bits to a new repo.
    #
    COUNTRY_CODES = [
        ('A1', _('Anonymous Proxy')),
        ('A2', _('Satellite Provider')),
        ('O1', _('Other Country')),
        ('AD', _('Andorra')),
        ('AE', _('United Arab Emirates')),
        ('AF', _('Afghanistan')),
        ('AG', _('Antigua and Barbuda')),
        ('AI', _('Anguilla')),
        ('AL', _('Albania')),
        ('AM', _('Armenia')),
        ('AO', _('Angola')),
        ('AP', _('Asia/Pacific Region')),
        ('AQ', _('Antarctica')),
        ('AR', _('Argentina')),
        ('AS', _('American Samoa')),
        ('AT', _('Austria')),
        ('AU', _('Australia')),
        ('AW', _('Aruba')),
        ('AX', _('Aland Islands')),
        ('AZ', _('Azerbaijan')),
        ('BA', _('Bosnia and Herzegovina')),
        ('BB', _('Barbados')),
        ('BD', _('Bangladesh')),
        ('BE', _('Belgium')),
        ('BF', _('Burkina Faso')),
        ('BG', _('Bulgaria')),
        ('BH', _('Bahrain')),
        ('BI', _('Burundi')),
        ('BJ', _('Benin')),
        ('BL', _('Saint Bartelemey')),
        ('BM', _('Bermuda')),
        ('BN', _('Brunei Darussalam')),
        ('BO', _('Bolivia')),
        ('BQ', _('Bonaire, Saint Eustatius and Saba')),
        ('BR', _('Brazil')),
        ('BS', _('Bahamas')),
        ('BT', _('Bhutan')),
        ('BV', _('Bouvet Island')),
        ('BW', _('Botswana')),
        ('BY', _('Belarus')),
        ('BZ', _('Belize')),
        ('CA', _('Canada')),
        ('CC', _('Cocos (Keeling) Islands')),
        ('CD', _('Congo, The Democratic Republic of the')),
        ('CF', _('Central African Republic')),
        ('CG', _('Congo')),
        ('CH', _('Switzerland')),
        ('CI', _('Cote d’Ivoire')),
        ('CK', _('Cook Islands')),
        ('CL', _('Chile')),
        ('CM', _('Cameroon')),
        ('CN', _('China')),
        ('CO', _('Colombia')),
        ('CR', _('Costa Rica')),
        ('CU', _('Cuba')),
        ('CV', _('Cape Verde')),
        ('CW', _('Curacao')),
        ('CX', _('Christmas Island')),
        ('CY', _('Cyprus')),
        ('CZ', _('Czech Republic')),
        ('DE', _('Germany')),
        ('DJ', _('Djibouti')),
        ('DK', _('Denmark')),
        ('DM', _('Dominica')),
        ('DO', _('Dominican Republic')),
        ('DZ', _('Algeria')),
        ('EC', _('Ecuador')),
        ('EE', _('Estonia')),
        ('EG', _('Egypt')),
        ('EH', _('Western Sahara')),
        ('ER', _('Eritrea')),
        ('ES', _('Spain')),
        ('ET', _('Ethiopia')),
        ('EU', _('Europe')),
        ('FI', _('Finland')),
        ('FJ', _('Fiji')),
        ('FK', _('Falkland Islands (Malvinas)')),
        ('FM', _('Micronesia, Federated States of')),
        ('FO', _('Faroe Islands')),
        ('FR', _('France')),
        ('GA', _('Gabon')),
        ('GB', _('United Kingdom')),
        ('GD', _('Grenada')),
        ('GE', _('Georgia')),
        ('GF', _('French Guiana')),
        ('GG', _('Guernsey')),
        ('GH', _('Ghana')),
        ('GI', _('Gibraltar')),
        ('GL', _('Greenland')),
        ('GM', _('Gambia')),
        ('GN', _('Guinea')),
        ('GP', _('Guadeloupe')),
        ('GQ', _('Equatorial Guinea')),
        ('GR', _('Greece')),
        ('GS', _('South Georgia and the South Sandwich Islands')),
        ('GT', _('Guatemala')),
        ('GU', _('Guam')),
        ('GW', _('Guinea-Bissau')),
        ('GY', _('Guyana')),
        ('HK', _('Hong Kong')),
        ('HM', _('Heard Island and McDonald Islands')),
        ('HN', _('Honduras')),
        ('HR', _('Croatia')),
        ('HT', _('Haiti')),
        ('HU', _('Hungary')),
        ('ID', _('Indonesia')),
        ('IE', _('Ireland')),
        ('IL', _('Israel')),
        ('IM', _('Isle of Man')),
        ('IN', _('India')),
        ('IO', _('British Indian Ocean Territory')),
        ('IQ', _('Iraq')),
        ('IR', _('Iran, Islamic Republic of')),
        ('IS', _('Iceland')),
        ('IT', _('Italy')),
        ('JE', _('Jersey')),
        ('JM', _('Jamaica')),
        ('JO', _('Jordan')),
        ('JP', _('Japan')),
        ('KE', _('Kenya')),
        ('KG', _('Kyrgyzstan')),
        ('KH', _('Cambodia')),
        ('KI', _('Kiribati')),
        ('KM', _('Comoros')),
        ('KN', _('Saint Kitts and Nevis')),
        ('KP', _('Korea, Democratic People’s Republic of')),
        ('KR', _('Korea, Republic of')),
        ('KW', _('Kuwait')),
        ('KY', _('Cayman Islands')),
        ('KZ', _('Kazakhstan')),
        ('LA', _('Lao, People’s Democratic Republic of')),
        ('LB', _('Lebanon')),
        ('LC', _('Saint Lucia')),
        ('LI', _('Liechtenstein')),
        ('LK', _('Sri Lanka')),
        ('LR', _('Liberia')),
        ('LS', _('Lesotho')),
        ('LT', _('Lithuania')),
        ('LU', _('Luxembourg')),
        ('LV', _('Latvia')),
        ('LY', _('Libyan Arab Jamahiriya')),
        ('MA', _('Morocco')),
        ('MC', _('Monaco')),
        ('MD', _('Moldova, Republic of')),
        ('ME', _('Montenegro')),
        ('MF', _('Saint Martin')),
        ('MG', _('Madagascar')),
        ('MH', _('Marshall Islands')),
        ('MK', _('Macedonia')),
        ('ML', _('Mali')),
        ('MM', _('Myanmar')),
        ('MN', _('Mongolia')),
        ('MO', _('Macao')),
        ('MP', _('Northern Mariana Islands')),
        ('MQ', _('Martinique')),
        ('MR', _('Mauritania')),
        ('MS', _('Montserrat')),
        ('MT', _('Malta')),
        ('MU', _('Mauritius')),
        ('MV', _('Maldives')),
        ('MW', _('Malawi')),
        ('MX', _('Mexico')),
        ('MY', _('Malaysia')),
        ('MZ', _('Mozambique')),
        ('NA', _('Namibia')),
        ('NC', _('New Caledonia')),
        ('NE', _('Niger')),
        ('NF', _('Norfolk Island')),
        ('NG', _('Nigeria')),
        ('NI', _('Nicaragua')),
        ('NL', _('Netherlands')),
        ('NO', _('Norway')),
        ('NP', _('Nepal')),
        ('NR', _('Nauru')),
        ('NU', _('Niue')),
        ('NZ', _('New Zealand')),
        ('OM', _('Oman')),
        ('PA', _('Panama')),
        ('PE', _('Peru')),
        ('PF', _('French Polynesia')),
        ('PG', _('Papua New Guinea')),
        ('PH', _('Philippines')),
        ('PK', _('Pakistan')),
        ('PL', _('Poland')),
        ('PM', _('Saint Pierre and Miquelon')),
        ('PN', _('Pitcairn')),
        ('PR', _('Puerto Rico')),
        ('PS', _('Palestinian Territory')),
        ('PT', _('Portugal')),
        ('PW', _('Palau')),
        ('PY', _('Paraguay')),
        ('QA', _('Qatar')),
        ('RE', _('Reunion')),
        ('RO', _('Romania')),
        ('RS', _('Serbia')),
        ('RU', _('Russian Federation')),
        ('RW', _('Rwanda')),
        ('SA', _('Saudi Arabia')),
        ('SB', _('Solomon Islands')),
        ('SC', _('Seychelles')),
        ('SD', _('Sudan')),
        ('SE', _('Sweden')),
        ('SG', _('Singapore')),
        ('SH', _('Saint Helena')),
        ('SI', _('Slovenia')),
        ('SJ', _('Svalbard and Jan Mayen')),
        ('SK', _('Slovakia')),
        ('SL', _('Sierra Leone')),
        ('SM', _('San Marino')),
        ('SN', _('Senegal')),
        ('SO', _('Somalia')),
        ('SR', _('Suriname')),
        ('SS', _('South Sudan')),
        ('ST', _('Sao Tome and Principe')),
        ('SV', _('El Salvador')),
        ('SX', _('Sint Maarten')),
        ('SY', _('Syrian Arab Republic')),
        ('SZ', _('Swaziland')),
        ('TC', _('Turks and Caicos Islands')),
        ('TD', _('Chad')),
        ('TF', _('French Southern Territories')),
        ('TG', _('Togo')),
        ('TH', _('Thailand')),
        ('TJ', _('Tajikistan')),
        ('TK', _('Tokelau')),
        ('TL', _('Timor-Leste')),
        ('TM', _('Turkmenistan')),
        ('TN', _('Tunisia')),
        ('TO', _('Tonga')),
        ('TR', _('Turkey')),
        ('TT', _('Trinidad and Tobago')),
        ('TV', _('Tuvalu')),
        ('TW', _('Taiwan')),
        ('TZ', _('Tanzania, United Republic of')),
        ('UA', _('Ukraine')),
        ('UG', _('Uganda')),
        ('UM', _('United States Minor Outlying Islands')),
        ('US', _('United States')),
        ('UY', _('Uruguay')),
        ('UZ', _('Uzbekistan')),
        ('VA', _('Holy See (Vatican City State)')),
        ('VC', _('Saint Vincent and the Grenadines')),
        ('VE', _('Venezuela')),
        ('VG', _('Virgin Islands, British')),
        ('VI', _('Virgin Islands, U.S.')),
        ('VN', _('Vietnam')),
        ('VU', _('Vanuatu')),
        ('WF', _('Wallis and Futuna')),
        ('WS', _('Samoa')),
        ('YE', _('Yemen')),
        ('YT', _('Mayotte')),
        ('ZA', _('South Africa')),
        ('ZM', _('Zambia')),
        ('ZW', _('Zimbabwe')),
    ]

    #
    # Since the user's locale may make these country names in non-alpha order,
    # We prepend the country code to the country name string for the field
    # choices.
    #
    COUNTRY_CODES_CHOICES = [ (code, _('%(code)s: %(name)s') % {
        'code': code, 'name': name
    }) for (code, name) in COUNTRY_CODES ]

    # This is so we can perform look-ups too.
    country_code_names = dict(COUNTRY_CODES)

    country_code = models.CharField(_('country'),
        blank=False,
        choices=COUNTRY_CODES_CHOICES,
        default='O1',  # 'Other Country'
        max_length=2,
    )

    @property
    def configuration_string(self):

        def wrapper():
            return _('{name} ({code})').format(name=self.country_code_names[self.country_code], code=self.country_code)

        return lazy(
            wrapper,
            six.text_type
        )()


class AuthenticatedSegmentPluginModel(SegmentBasePluginModel):

    @property
    def configuration_string(self):
        return _('is Authenticated')


@python_2_unicode_compatible
class Segment(models.Model):
    '''
    This is a hollow, unmanaged model that simply allows us to attach custom
    admin views into the AdminSite.
    '''

    class Meta:
        managed=False

    def __str__(self):
        return 'Segment is an empty, unmanaged model.'