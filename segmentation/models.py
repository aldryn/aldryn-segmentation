# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from cms.models import CMSPlugin

#
# NOTE: The SegmentLimitPluginModel does NOT subclass SegmentBasePluginModel
#
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
        help_text=ugettext('Display up to how many matching segments?'),
    )

    @property
    def configuration_string(self):
        if self.max_children == 0:
            return _(u'Show All')
        elif self.max_children == 1:
            return _(u'Show First')
        else:
            return _(u'Show First %d' % self.max_children)


    def __unicode__(self):
        if self.label:
            return _(u'%(label)s [%(config)s]') % {
                'label': self.label,
                'config': self.configuration_string,
            }
        else:
            return self.configuration_string


class SegmentBasePluginModel(CMSPlugin):
    '''
    Defines a common interface for segment plugins. Also note that plugin
    model's subclassing this class will automatically be (un-)registered
    (from)to the segment_pool via 'pre_delete' and 'post_save' signals. This
    is implemented in segmentation.segment_pool.
    '''

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
        Return a ugettext_lazy object that represents the configuration for
        the plugin instance in a unique, concise manner that is suitable for a
        toolbar menu option.

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

        NOTE: Each subclass must override to suit.
        '''
        raise NotImplementedError("Please Implement this method")


    def __unicode__(self):
        if self.label:
            return _(u'%(label)s [%(config)s]') % {
                'label': self.label,
                'config': self.configuration_string,
            }
        else:
            return self.configuration_string


class FallbackSegmentPluginModel(SegmentBasePluginModel):

    @property
    def configuration_string(self):
        return _(u'Always active')


class SwitchSegmentPluginModel(SegmentBasePluginModel):

    on_off = models.BooleanField(_('Always on?'),
        default=True,
        help_text=_('Uncheck to always hide child plugins.'),
    )

    @property
    def configuration_string(self):
        if self.on_off:
            return _(u'Always ON')
        else:
            return _(u'Always OFF')


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
        return _(u'“%(key)s” equals “%(value)s”' % {
            'key': self.cookie_key,
            'value': self.cookie_value,
        })


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
        (u'A1', _(u'Anonymous Proxy')),
        (u'A2', _(u'Satellite Provider')),
        (u'O1', _(u'Other Country')),
        (u'AD', _(u'Andorra')),
        (u'AE', _(u'United Arab Emirates')),
        (u'AF', _(u'Afghanistan')),
        (u'AG', _(u'Antigua and Barbuda')),
        (u'AI', _(u'Anguilla')),
        (u'AL', _(u'Albania')),
        (u'AM', _(u'Armenia')),
        (u'AO', _(u'Angola')),
        (u'AP', _(u'Asia/Pacific Region')),
        (u'AQ', _(u'Antarctica')),
        (u'AR', _(u'Argentina')),
        (u'AS', _(u'American Samoa')),
        (u'AT', _(u'Austria')),
        (u'AU', _(u'Australia')),
        (u'AW', _(u'Aruba')),
        (u'AX', _(u'Aland Islands')),
        (u'AZ', _(u'Azerbaijan')),
        (u'BA', _(u'Bosnia and Herzegovina')),
        (u'BB', _(u'Barbados')),
        (u'BD', _(u'Bangladesh')),
        (u'BE', _(u'Belgium')),
        (u'BF', _(u'Burkina Faso')),
        (u'BG', _(u'Bulgaria')),
        (u'BH', _(u'Bahrain')),
        (u'BI', _(u'Burundi')),
        (u'BJ', _(u'Benin')),
        (u'BL', _(u'Saint Bartelemey')),
        (u'BM', _(u'Bermuda')),
        (u'BN', _(u'Brunei Darussalam')),
        (u'BO', _(u'Bolivia')),
        (u'BQ', _(u'Bonaire, Saint Eustatius and Saba')),
        (u'BR', _(u'Brazil')),
        (u'BS', _(u'Bahamas')),
        (u'BT', _(u'Bhutan')),
        (u'BV', _(u'Bouvet Island')),
        (u'BW', _(u'Botswana')),
        (u'BY', _(u'Belarus')),
        (u'BZ', _(u'Belize')),
        (u'CA', _(u'Canada')),
        (u'CC', _(u'Cocos (Keeling) Islands')),
        (u'CD', _(u'Congo, The Democratic Republic of the')),
        (u'CF', _(u'Central African Republic')),
        (u'CG', _(u'Congo')),
        (u'CH', _(u'Switzerland')),
        (u'CI', _(u'Cote d’Ivoire')),
        (u'CK', _(u'Cook Islands')),
        (u'CL', _(u'Chile')),
        (u'CM', _(u'Cameroon')),
        (u'CN', _(u'China')),
        (u'CO', _(u'Colombia')),
        (u'CR', _(u'Costa Rica')),
        (u'CU', _(u'Cuba')),
        (u'CV', _(u'Cape Verde')),
        (u'CW', _(u'Curacao')),
        (u'CX', _(u'Christmas Island')),
        (u'CY', _(u'Cyprus')),
        (u'CZ', _(u'Czech Republic')),
        (u'DE', _(u'Germany')),
        (u'DJ', _(u'Djibouti')),
        (u'DK', _(u'Denmark')),
        (u'DM', _(u'Dominica')),
        (u'DO', _(u'Dominican Republic')),
        (u'DZ', _(u'Algeria')),
        (u'EC', _(u'Ecuador')),
        (u'EE', _(u'Estonia')),
        (u'EG', _(u'Egypt')),
        (u'EH', _(u'Western Sahara')),
        (u'ER', _(u'Eritrea')),
        (u'ES', _(u'Spain')),
        (u'ET', _(u'Ethiopia')),
        (u'EU', _(u'Europe')),
        (u'FI', _(u'Finland')),
        (u'FJ', _(u'Fiji')),
        (u'FK', _(u'Falkland Islands (Malvinas)')),
        (u'FM', _(u'Micronesia, Federated States of')),
        (u'FO', _(u'Faroe Islands')),
        (u'FR', _(u'France')),
        (u'GA', _(u'Gabon')),
        (u'GB', _(u'United Kingdom')),
        (u'GD', _(u'Grenada')),
        (u'GE', _(u'Georgia')),
        (u'GF', _(u'French Guiana')),
        (u'GG', _(u'Guernsey')),
        (u'GH', _(u'Ghana')),
        (u'GI', _(u'Gibraltar')),
        (u'GL', _(u'Greenland')),
        (u'GM', _(u'Gambia')),
        (u'GN', _(u'Guinea')),
        (u'GP', _(u'Guadeloupe')),
        (u'GQ', _(u'Equatorial Guinea')),
        (u'GR', _(u'Greece')),
        (u'GS', _(u'South Georgia and the South Sandwich Islands')),
        (u'GT', _(u'Guatemala')),
        (u'GU', _(u'Guam')),
        (u'GW', _(u'Guinea-Bissau')),
        (u'GY', _(u'Guyana')),
        (u'HK', _(u'Hong Kong')),
        (u'HM', _(u'Heard Island and McDonald Islands')),
        (u'HN', _(u'Honduras')),
        (u'HR', _(u'Croatia')),
        (u'HT', _(u'Haiti')),
        (u'HU', _(u'Hungary')),
        (u'ID', _(u'Indonesia')),
        (u'IE', _(u'Ireland')),
        (u'IL', _(u'Israel')),
        (u'IM', _(u'Isle of Man')),
        (u'IN', _(u'India')),
        (u'IO', _(u'British Indian Ocean Territory')),
        (u'IQ', _(u'Iraq')),
        (u'IR', _(u'Iran, Islamic Republic of')),
        (u'IS', _(u'Iceland')),
        (u'IT', _(u'Italy')),
        (u'JE', _(u'Jersey')),
        (u'JM', _(u'Jamaica')),
        (u'JO', _(u'Jordan')),
        (u'JP', _(u'Japan')),
        (u'KE', _(u'Kenya')),
        (u'KG', _(u'Kyrgyzstan')),
        (u'KH', _(u'Cambodia')),
        (u'KI', _(u'Kiribati')),
        (u'KM', _(u'Comoros')),
        (u'KN', _(u'Saint Kitts and Nevis')),
        (u'KP', _(u'Korea, Democratic People’s Republic of')),
        (u'KR', _(u'Korea, Republic of')),
        (u'KW', _(u'Kuwait')),
        (u'KY', _(u'Cayman Islands')),
        (u'KZ', _(u'Kazakhstan')),
        (u'LA', _(u'Lao, People’s Democratic Republic of')),
        (u'LB', _(u'Lebanon')),
        (u'LC', _(u'Saint Lucia')),
        (u'LI', _(u'Liechtenstein')),
        (u'LK', _(u'Sri Lanka')),
        (u'LR', _(u'Liberia')),
        (u'LS', _(u'Lesotho')),
        (u'LT', _(u'Lithuania')),
        (u'LU', _(u'Luxembourg')),
        (u'LV', _(u'Latvia')),
        (u'LY', _(u'Libyan Arab Jamahiriya')),
        (u'MA', _(u'Morocco')),
        (u'MC', _(u'Monaco')),
        (u'MD', _(u'Moldova, Republic of')),
        (u'ME', _(u'Montenegro')),
        (u'MF', _(u'Saint Martin')),
        (u'MG', _(u'Madagascar')),
        (u'MH', _(u'Marshall Islands')),
        (u'MK', _(u'Macedonia')),
        (u'ML', _(u'Mali')),
        (u'MM', _(u'Myanmar')),
        (u'MN', _(u'Mongolia')),
        (u'MO', _(u'Macao')),
        (u'MP', _(u'Northern Mariana Islands')),
        (u'MQ', _(u'Martinique')),
        (u'MR', _(u'Mauritania')),
        (u'MS', _(u'Montserrat')),
        (u'MT', _(u'Malta')),
        (u'MU', _(u'Mauritius')),
        (u'MV', _(u'Maldives')),
        (u'MW', _(u'Malawi')),
        (u'MX', _(u'Mexico')),
        (u'MY', _(u'Malaysia')),
        (u'MZ', _(u'Mozambique')),
        (u'NA', _(u'Namibia')),
        (u'NC', _(u'New Caledonia')),
        (u'NE', _(u'Niger')),
        (u'NF', _(u'Norfolk Island')),
        (u'NG', _(u'Nigeria')),
        (u'NI', _(u'Nicaragua')),
        (u'NL', _(u'Netherlands')),
        (u'NO', _(u'Norway')),
        (u'NP', _(u'Nepal')),
        (u'NR', _(u'Nauru')),
        (u'NU', _(u'Niue')),
        (u'NZ', _(u'New Zealand')),
        (u'OM', _(u'Oman')),
        (u'PA', _(u'Panama')),
        (u'PE', _(u'Peru')),
        (u'PF', _(u'French Polynesia')),
        (u'PG', _(u'Papua New Guinea')),
        (u'PH', _(u'Philippines')),
        (u'PK', _(u'Pakistan')),
        (u'PL', _(u'Poland')),
        (u'PM', _(u'Saint Pierre and Miquelon')),
        (u'PN', _(u'Pitcairn')),
        (u'PR', _(u'Puerto Rico')),
        (u'PS', _(u'Palestinian Territory')),
        (u'PT', _(u'Portugal')),
        (u'PW', _(u'Palau')),
        (u'PY', _(u'Paraguay')),
        (u'QA', _(u'Qatar')),
        (u'RE', _(u'Reunion')),
        (u'RO', _(u'Romania')),
        (u'RS', _(u'Serbia')),
        (u'RU', _(u'Russian Federation')),
        (u'RW', _(u'Rwanda')),
        (u'SA', _(u'Saudi Arabia')),
        (u'SB', _(u'Solomon Islands')),
        (u'SC', _(u'Seychelles')),
        (u'SD', _(u'Sudan')),
        (u'SE', _(u'Sweden')),
        (u'SG', _(u'Singapore')),
        (u'SH', _(u'Saint Helena')),
        (u'SI', _(u'Slovenia')),
        (u'SJ', _(u'Svalbard and Jan Mayen')),
        (u'SK', _(u'Slovakia')),
        (u'SL', _(u'Sierra Leone')),
        (u'SM', _(u'San Marino')),
        (u'SN', _(u'Senegal')),
        (u'SO', _(u'Somalia')),
        (u'SR', _(u'Suriname')),
        (u'SS', _(u'South Sudan')),
        (u'ST', _(u'Sao Tome and Principe')),
        (u'SV', _(u'El Salvador')),
        (u'SX', _(u'Sint Maarten')),
        (u'SY', _(u'Syrian Arab Republic')),
        (u'SZ', _(u'Swaziland')),
        (u'TC', _(u'Turks and Caicos Islands')),
        (u'TD', _(u'Chad')),
        (u'TF', _(u'French Southern Territories')),
        (u'TG', _(u'Togo')),
        (u'TH', _(u'Thailand')),
        (u'TJ', _(u'Tajikistan')),
        (u'TK', _(u'Tokelau')),
        (u'TL', _(u'Timor-Leste')),
        (u'TM', _(u'Turkmenistan')),
        (u'TN', _(u'Tunisia')),
        (u'TO', _(u'Tonga')),
        (u'TR', _(u'Turkey')),
        (u'TT', _(u'Trinidad and Tobago')),
        (u'TV', _(u'Tuvalu')),
        (u'TW', _(u'Taiwan')),
        (u'TZ', _(u'Tanzania, United Republic of')),
        (u'UA', _(u'Ukraine')),
        (u'UG', _(u'Uganda')),
        (u'UM', _(u'United States Minor Outlying Islands')),
        (u'US', _(u'United States')),
        (u'UY', _(u'Uruguay')),
        (u'UZ', _(u'Uzbekistan')),
        (u'VA', _(u'Holy See (Vatican City State)')),
        (u'VC', _(u'Saint Vincent and the Grenadines')),
        (u'VE', _(u'Venezuela')),
        (u'VG', _(u'Virgin Islands, British')),
        (u'VI', _(u'Virgin Islands, U.S.')),
        (u'VN', _(u'Vietnam')),
        (u'VU', _(u'Vanuatu')),
        (u'WF', _(u'Wallis and Futuna')),
        (u'WS', _(u'Samoa')),
        (u'YE', _(u'Yemen')),
        (u'YT', _(u'Mayotte')),
        (u'ZA', _(u'South Africa')),
        (u'ZM', _(u'Zambia')),
        (u'ZW', _(u'Zimbabwe')),
    ]

    #
    # Since the user's locale may make these country names in non-alpha order,
    # We prepend the country code to the country name string.
    #
    COUNTRY_CODES = [ (code, _(u'%(code)s: %(name)s') % {
        'code': code, 'name': name
    }) for (code, name) in COUNTRY_CODES ]

    # This is so we can perform look-ups too.
    country_code_names = dict(COUNTRY_CODES)

    country_code = models.CharField(_('country'),
        blank=False,
        choices=COUNTRY_CODES,
        default='O1',  # 'Other Country'
        max_length=2,
    )

    @property
    def configuration_string(self):
        return _(u'%(name)s (%(code)s)' % {
            'name': self.country_code_names[self.country_code],
            'code': self.country_code,
        })


class AuthenticatedSegmentPluginModel(SegmentBasePluginModel):

    dummy = models.CharField(max_length=10, blank=True)

    @property
    def configuration_string(self):
        return _(u'is Authenticated')


class Segment(models.Model):
    '''
    This is a hollow, unmanaged model that simply allows us to attach custom
    admin views into the AdminSite.
    '''

    class Meta:
        managed=False
