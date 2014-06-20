# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy, ugettext_noop

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

    label = models.CharField(ugettext_lazy('label'),
        blank=True,
        default='',
        help_text=ugettext_lazy('Optionally set a label for this limit block.'),
        max_length=128,
    )

    max_children = models.PositiveIntegerField(ugettext_lazy('# of matches to display'),
        blank=False,
        default=1,
        help_text=ugettext('Display up to how many matching segments?'),
    )

    @property
    def configuration_string(self):
        if self.max_children == 0:
            return ugettext_noop(u'Show All')
        elif self.max_children == 1:
            return ugettext_noop(u'Show First')
        else:
            return ugettext_noop(u'Show First %d') % self.max_children


    def __unicode__(self):
        if self.label:
            return ugettext_lazy(u'%(label)s [%(config)s]') % {
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

    label = models.CharField(ugettext_lazy('label'),
        blank=True,
        default='',
        max_length=128,
    )


    @property
    def configuration_string(self):
        '''
        Return a ugettextugettext_lazy object that represents the configuration for the
        plugin instance in a unique, concise manner that is suitable for a
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
            return ugettext_lazy(u'%(label)s [%(config)s]') % {
                'label': self.label,
                'config': self.configuration_string,
            }
        else:
            return self.configuration_string


class FallbackSegmentPluginModel(SegmentBasePluginModel):

    @property
    def configuration_string(self):
        return ugettext_noop(u'Always active')


class SwitchSegmentPluginModel(SegmentBasePluginModel):

    on_off = models.BooleanField(ugettext_lazy('Always on?'),
        default=True,
        help_text=ugettext_lazy('Uncheck to always hide child plugins.'),
    )

    @property
    def configuration_string(self):
        if self.on_off:
            return ugettext_noop(u'Always ON')
        else:
            return ugettext_noop(u'Always OFF')


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

    cookie_key = models.CharField(ugettext_lazy('name of cookie'),
        blank=False,
        default='',
        help_text=ugettext_lazy('Name of cookie to consider.'),
        max_length=4096,
    )

    cookie_value = models.CharField(ugettext_lazy('value to compare'),
        blank=False,
        default='',
        help_text=ugettext_lazy('Value to consider.'),
        max_length=4096,
    )

    @property
    def configuration_string(self):
        return ugettext_noop(u'“%(key)s” equals “%(value)s”') % {
            'key': self.cookie_key,
            'value': self.cookie_value,
        }


class CountrySegmentPluginModel(SegmentBasePluginModel):

    #
    # NOTE: This list is derived from MaxMind's datasets
    # (http://dev.maxmind.com/geoip/legacy/codes/iso3166/), so contains non-
    # country entities such as "A1", "A2", "O1" as well pseudo-countries such as
    # "EU", "AP" etc. These are very relevant to this implementation.
    #
    # MaxMind also state:
    # Please note that "EU" and "AP" codes are only used when a specific country
    # code has not been designated (see FAQ). Blocking or re-directing by "EU" or
    # "AP" will only affect a small portion of IP addresses. Instead, you should
    # list the countries you want to block/re- direct individually.
    #
    # TODO: Move this and related bits to a new repo.
    # TODO: How do we make this internationalized?
    #
    COUNTRY_CODES = [
        (u'A1', ugettext_lazy(u'Anonymous Proxy')),
        (u'A2', ugettext_lazy(u'Satellite Provider')),
        (u'O1', ugettext_lazy(u'Other Country')),
        (u'AD', ugettext_lazy(u'Andorra')),
        (u'AE', ugettext_lazy(u'United Arab Emirates')),
        (u'AF', ugettext_lazy(u'Afghanistan')),
        (u'AG', ugettext_lazy(u'Antigua and Barbuda')),
        (u'AI', ugettext_lazy(u'Anguilla')),
        (u'AL', ugettext_lazy(u'Albania')),
        (u'AM', ugettext_lazy(u'Armenia')),
        (u'AO', ugettext_lazy(u'Angola')),
        (u'AP', ugettext_lazy(u'Asia/Pacific Region')),
        (u'AQ', ugettext_lazy(u'Antarctica')),
        (u'AR', ugettext_lazy(u'Argentina')),
        (u'AS', ugettext_lazy(u'American Samoa')),
        (u'AT', ugettext_lazy(u'Austria')),
        (u'AU', ugettext_lazy(u'Australia')),
        (u'AW', ugettext_lazy(u'Aruba')),
        (u'AX', ugettext_lazy(u'Aland Islands')),
        (u'AZ', ugettext_lazy(u'Azerbaijan')),
        (u'BA', ugettext_lazy(u'Bosnia and Herzegovina')),
        (u'BB', ugettext_lazy(u'Barbados')),
        (u'BD', ugettext_lazy(u'Bangladesh')),
        (u'BE', ugettext_lazy(u'Belgium')),
        (u'BF', ugettext_lazy(u'Burkina Faso')),
        (u'BG', ugettext_lazy(u'Bulgaria')),
        (u'BH', ugettext_lazy(u'Bahrain')),
        (u'BI', ugettext_lazy(u'Burundi')),
        (u'BJ', ugettext_lazy(u'Benin')),
        (u'BL', ugettext_lazy(u'Saint Bartelemey')),
        (u'BM', ugettext_lazy(u'Bermuda')),
        (u'BN', ugettext_lazy(u'Brunei Darussalam')),
        (u'BO', ugettext_lazy(u'Bolivia')),
        (u'BQ', ugettext_lazy(u'Bonaire, Saint Eustatius and Saba')),
        (u'BR', ugettext_lazy(u'Brazil')),
        (u'BS', ugettext_lazy(u'Bahamas')),
        (u'BT', ugettext_lazy(u'Bhutan')),
        (u'BV', ugettext_lazy(u'Bouvet Island')),
        (u'BW', ugettext_lazy(u'Botswana')),
        (u'BY', ugettext_lazy(u'Belarus')),
        (u'BZ', ugettext_lazy(u'Belize')),
        (u'CA', ugettext_lazy(u'Canada')),
        (u'CC', ugettext_lazy(u'Cocos (Keeling) Islands')),
        (u'CD', ugettext_lazy(u'Congo, The Democratic Republic of the')),
        (u'CF', ugettext_lazy(u'Central African Republic')),
        (u'CG', ugettext_lazy(u'Congo')),
        (u'CH', ugettext_lazy(u'Switzerland')),
        (u'CI', ugettext_lazy(u'Cote d’Ivoire')),
        (u'CK', ugettext_lazy(u'Cook Islands')),
        (u'CL', ugettext_lazy(u'Chile')),
        (u'CM', ugettext_lazy(u'Cameroon')),
        (u'CN', ugettext_lazy(u'China')),
        (u'CO', ugettext_lazy(u'Colombia')),
        (u'CR', ugettext_lazy(u'Costa Rica')),
        (u'CU', ugettext_lazy(u'Cuba')),
        (u'CV', ugettext_lazy(u'Cape Verde')),
        (u'CW', ugettext_lazy(u'Curacao')),
        (u'CX', ugettext_lazy(u'Christmas Island')),
        (u'CY', ugettext_lazy(u'Cyprus')),
        (u'CZ', ugettext_lazy(u'Czech Republic')),
        (u'DE', ugettext_lazy(u'Germany')),
        (u'DJ', ugettext_lazy(u'Djibouti')),
        (u'DK', ugettext_lazy(u'Denmark')),
        (u'DM', ugettext_lazy(u'Dominica')),
        (u'DO', ugettext_lazy(u'Dominican Republic')),
        (u'DZ', ugettext_lazy(u'Algeria')),
        (u'EC', ugettext_lazy(u'Ecuador')),
        (u'EE', ugettext_lazy(u'Estonia')),
        (u'EG', ugettext_lazy(u'Egypt')),
        (u'EH', ugettext_lazy(u'Western Sahara')),
        (u'ER', ugettext_lazy(u'Eritrea')),
        (u'ES', ugettext_lazy(u'Spain')),
        (u'ET', ugettext_lazy(u'Ethiopia')),
        (u'EU', ugettext_lazy(u'Europe')),
        (u'FI', ugettext_lazy(u'Finland')),
        (u'FJ', ugettext_lazy(u'Fiji')),
        (u'FK', ugettext_lazy(u'Falkland Islands (Malvinas)')),
        (u'FM', ugettext_lazy(u'Micronesia, Federated States of')),
        (u'FO', ugettext_lazy(u'Faroe Islands')),
        (u'FR', ugettext_lazy(u'France')),
        (u'GA', ugettext_lazy(u'Gabon')),
        (u'GB', ugettext_lazy(u'United Kingdom')),
        (u'GD', ugettext_lazy(u'Grenada')),
        (u'GE', ugettext_lazy(u'Georgia')),
        (u'GF', ugettext_lazy(u'French Guiana')),
        (u'GG', ugettext_lazy(u'Guernsey')),
        (u'GH', ugettext_lazy(u'Ghana')),
        (u'GI', ugettext_lazy(u'Gibraltar')),
        (u'GL', ugettext_lazy(u'Greenland')),
        (u'GM', ugettext_lazy(u'Gambia')),
        (u'GN', ugettext_lazy(u'Guinea')),
        (u'GP', ugettext_lazy(u'Guadeloupe')),
        (u'GQ', ugettext_lazy(u'Equatorial Guinea')),
        (u'GR', ugettext_lazy(u'Greece')),
        (u'GS', ugettext_lazy(u'South Georgia and the South Sandwich Islands')),
        (u'GT', ugettext_lazy(u'Guatemala')),
        (u'GU', ugettext_lazy(u'Guam')),
        (u'GW', ugettext_lazy(u'Guinea-Bissau')),
        (u'GY', ugettext_lazy(u'Guyana')),
        (u'HK', ugettext_lazy(u'Hong Kong')),
        (u'HM', ugettext_lazy(u'Heard Island and McDonald Islands')),
        (u'HN', ugettext_lazy(u'Honduras')),
        (u'HR', ugettext_lazy(u'Croatia')),
        (u'HT', ugettext_lazy(u'Haiti')),
        (u'HU', ugettext_lazy(u'Hungary')),
        (u'ID', ugettext_lazy(u'Indonesia')),
        (u'IE', ugettext_lazy(u'Ireland')),
        (u'IL', ugettext_lazy(u'Israel')),
        (u'IM', ugettext_lazy(u'Isle of Man')),
        (u'IN', ugettext_lazy(u'India')),
        (u'IO', ugettext_lazy(u'British Indian Ocean Territory')),
        (u'IQ', ugettext_lazy(u'Iraq')),
        (u'IR', ugettext_lazy(u'Iran, Islamic Republic of')),
        (u'IS', ugettext_lazy(u'Iceland')),
        (u'IT', ugettext_lazy(u'Italy')),
        (u'JE', ugettext_lazy(u'Jersey')),
        (u'JM', ugettext_lazy(u'Jamaica')),
        (u'JO', ugettext_lazy(u'Jordan')),
        (u'JP', ugettext_lazy(u'Japan')),
        (u'KE', ugettext_lazy(u'Kenya')),
        (u'KG', ugettext_lazy(u'Kyrgyzstan')),
        (u'KH', ugettext_lazy(u'Cambodia')),
        (u'KI', ugettext_lazy(u'Kiribati')),
        (u'KM', ugettext_lazy(u'Comoros')),
        (u'KN', ugettext_lazy(u'Saint Kitts and Nevis')),
        (u'KP', ugettext_lazy(u'Korea, Democratic People’s Republic of')),
        (u'KR', ugettext_lazy(u'Korea, Republic of')),
        (u'KW', ugettext_lazy(u'Kuwait')),
        (u'KY', ugettext_lazy(u'Cayman Islands')),
        (u'KZ', ugettext_lazy(u'Kazakhstan')),
        (u'LA', ugettext_lazy(u'Lao, People’s Democratic Republic of')),
        (u'LB', ugettext_lazy(u'Lebanon')),
        (u'LC', ugettext_lazy(u'Saint Lucia')),
        (u'LI', ugettext_lazy(u'Liechtenstein')),
        (u'LK', ugettext_lazy(u'Sri Lanka')),
        (u'LR', ugettext_lazy(u'Liberia')),
        (u'LS', ugettext_lazy(u'Lesotho')),
        (u'LT', ugettext_lazy(u'Lithuania')),
        (u'LU', ugettext_lazy(u'Luxembourg')),
        (u'LV', ugettext_lazy(u'Latvia')),
        (u'LY', ugettext_lazy(u'Libyan Arab Jamahiriya')),
        (u'MA', ugettext_lazy(u'Morocco')),
        (u'MC', ugettext_lazy(u'Monaco')),
        (u'MD', ugettext_lazy(u'Moldova, Republic of')),
        (u'ME', ugettext_lazy(u'Montenegro')),
        (u'MF', ugettext_lazy(u'Saint Martin')),
        (u'MG', ugettext_lazy(u'Madagascar')),
        (u'MH', ugettext_lazy(u'Marshall Islands')),
        (u'MK', ugettext_lazy(u'Macedonia')),
        (u'ML', ugettext_lazy(u'Mali')),
        (u'MM', ugettext_lazy(u'Myanmar')),
        (u'MN', ugettext_lazy(u'Mongolia')),
        (u'MO', ugettext_lazy(u'Macao')),
        (u'MP', ugettext_lazy(u'Northern Mariana Islands')),
        (u'MQ', ugettext_lazy(u'Martinique')),
        (u'MR', ugettext_lazy(u'Mauritania')),
        (u'MS', ugettext_lazy(u'Montserrat')),
        (u'MT', ugettext_lazy(u'Malta')),
        (u'MU', ugettext_lazy(u'Mauritius')),
        (u'MV', ugettext_lazy(u'Maldives')),
        (u'MW', ugettext_lazy(u'Malawi')),
        (u'MX', ugettext_lazy(u'Mexico')),
        (u'MY', ugettext_lazy(u'Malaysia')),
        (u'MZ', ugettext_lazy(u'Mozambique')),
        (u'NA', ugettext_lazy(u'Namibia')),
        (u'NC', ugettext_lazy(u'New Caledonia')),
        (u'NE', ugettext_lazy(u'Niger')),
        (u'NF', ugettext_lazy(u'Norfolk Island')),
        (u'NG', ugettext_lazy(u'Nigeria')),
        (u'NI', ugettext_lazy(u'Nicaragua')),
        (u'NL', ugettext_lazy(u'Netherlands')),
        (u'NO', ugettext_lazy(u'Norway')),
        (u'NP', ugettext_lazy(u'Nepal')),
        (u'NR', ugettext_lazy(u'Nauru')),
        (u'NU', ugettext_lazy(u'Niue')),
        (u'NZ', ugettext_lazy(u'New Zealand')),
        (u'OM', ugettext_lazy(u'Oman')),
        (u'PA', ugettext_lazy(u'Panama')),
        (u'PE', ugettext_lazy(u'Peru')),
        (u'PF', ugettext_lazy(u'French Polynesia')),
        (u'PG', ugettext_lazy(u'Papua New Guinea')),
        (u'PH', ugettext_lazy(u'Philippines')),
        (u'PK', ugettext_lazy(u'Pakistan')),
        (u'PL', ugettext_lazy(u'Poland')),
        (u'PM', ugettext_lazy(u'Saint Pierre and Miquelon')),
        (u'PN', ugettext_lazy(u'Pitcairn')),
        (u'PR', ugettext_lazy(u'Puerto Rico')),
        (u'PS', ugettext_lazy(u'Palestinian Territory')),
        (u'PT', ugettext_lazy(u'Portugal')),
        (u'PW', ugettext_lazy(u'Palau')),
        (u'PY', ugettext_lazy(u'Paraguay')),
        (u'QA', ugettext_lazy(u'Qatar')),
        (u'RE', ugettext_lazy(u'Reunion')),
        (u'RO', ugettext_lazy(u'Romania')),
        (u'RS', ugettext_lazy(u'Serbia')),
        (u'RU', ugettext_lazy(u'Russian Federation')),
        (u'RW', ugettext_lazy(u'Rwanda')),
        (u'SA', ugettext_lazy(u'Saudi Arabia')),
        (u'SB', ugettext_lazy(u'Solomon Islands')),
        (u'SC', ugettext_lazy(u'Seychelles')),
        (u'SD', ugettext_lazy(u'Sudan')),
        (u'SE', ugettext_lazy(u'Sweden')),
        (u'SG', ugettext_lazy(u'Singapore')),
        (u'SH', ugettext_lazy(u'Saint Helena')),
        (u'SI', ugettext_lazy(u'Slovenia')),
        (u'SJ', ugettext_lazy(u'Svalbard and Jan Mayen')),
        (u'SK', ugettext_lazy(u'Slovakia')),
        (u'SL', ugettext_lazy(u'Sierra Leone')),
        (u'SM', ugettext_lazy(u'San Marino')),
        (u'SN', ugettext_lazy(u'Senegal')),
        (u'SO', ugettext_lazy(u'Somalia')),
        (u'SR', ugettext_lazy(u'Suriname')),
        (u'SS', ugettext_lazy(u'South Sudan')),
        (u'ST', ugettext_lazy(u'Sao Tome and Principe')),
        (u'SV', ugettext_lazy(u'El Salvador')),
        (u'SX', ugettext_lazy(u'Sint Maarten')),
        (u'SY', ugettext_lazy(u'Syrian Arab Republic')),
        (u'SZ', ugettext_lazy(u'Swaziland')),
        (u'TC', ugettext_lazy(u'Turks and Caicos Islands')),
        (u'TD', ugettext_lazy(u'Chad')),
        (u'TF', ugettext_lazy(u'French Southern Territories')),
        (u'TG', ugettext_lazy(u'Togo')),
        (u'TH', ugettext_lazy(u'Thailand')),
        (u'TJ', ugettext_lazy(u'Tajikistan')),
        (u'TK', ugettext_lazy(u'Tokelau')),
        (u'TL', ugettext_lazy(u'Timor-Leste')),
        (u'TM', ugettext_lazy(u'Turkmenistan')),
        (u'TN', ugettext_lazy(u'Tunisia')),
        (u'TO', ugettext_lazy(u'Tonga')),
        (u'TR', ugettext_lazy(u'Turkey')),
        (u'TT', ugettext_lazy(u'Trinidad and Tobago')),
        (u'TV', ugettext_lazy(u'Tuvalu')),
        (u'TW', ugettext_lazy(u'Taiwan')),
        (u'TZ', ugettext_lazy(u'Tanzania, United Republic of')),
        (u'UA', ugettext_lazy(u'Ukraine')),
        (u'UG', ugettext_lazy(u'Uganda')),
        (u'UM', ugettext_lazy(u'United States Minor Outlying Islands')),
        (u'US', ugettext_lazy(u'United States')),
        (u'UY', ugettext_lazy(u'Uruguay')),
        (u'UZ', ugettext_lazy(u'Uzbekistan')),
        (u'VA', ugettext_lazy(u'Holy See (Vatican City State)')),
        (u'VC', ugettext_lazy(u'Saint Vincent and the Grenadines')),
        (u'VE', ugettext_lazy(u'Venezuela')),
        (u'VG', ugettext_lazy(u'Virgin Islands, British')),
        (u'VI', ugettext_lazy(u'Virgin Islands, U.S.')),
        (u'VN', ugettext_lazy(u'Vietnam')),
        (u'VU', ugettext_lazy(u'Vanuatu')),
        (u'WF', ugettext_lazy(u'Wallis and Futuna')),
        (u'WS', ugettext_lazy(u'Samoa')),
        (u'YE', ugettext_lazy(u'Yemen')),
        (u'YT', ugettext_lazy(u'Mayotte')),
        (u'ZA', ugettext_lazy(u'South Africa')),
        (u'ZM', ugettext_lazy(u'Zambia')),
        (u'ZW', ugettext_lazy(u'Zimbabwe')),
    ]

    #
    # Since the user's locale may make these country names in non-alpha order,
    # We prepend the country code to the country name string.
    #
    COUNTRY_CODES = [ (code, ugettext_lazy(u'%(code)s: %(name)s') % {
        'code': code, 'name': name
    }) for (code, name) in COUNTRY_CODES ]

    # This is so we can perform look-ups too.
    country_code_names = dict(COUNTRY_CODES)

    country_code = models.CharField(ugettext_lazy('country'),
        blank=False,
        choices=COUNTRY_CODES,
        default='O1',  # 'Other Country'
        max_length=2,
    )

    @property
    def configuration_string(self):
        return ugettext_noop(u'%(name)s (%(code)s)') % {
            'name': self.country_code_names[self.country_code],
            'code': self.country_code,
        }


class AuthenticatedSegmentPluginModel(SegmentBasePluginModel):

    dummy = models.CharField(max_length=10, blank=True)

    @property
    def configuration_string(self):
        return ugettext_noop(u'is Authenticated')


class Segment(models.Model):
    '''
    This is a hollow, unmanaged model that simply allows us to attach custom
    admin views into the AdminSite.
    '''

    class Meta:
        managed=False
