# -*- coding: utf-8 -*-

from operator import itemgetter

from django.db import models
from django.utils.translation import ugettext_lazy as _

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
        help_text=_('Display up to how many matching segments?'),
    )

    @property
    def configuration_string(self):
        if self.max_children == 0:
            return u'Show All'
        elif self.max_children == 1:
            return u'Show First'
        else:
            return u'Show First %d' % self.max_children


    def __unicode__(self):
        if self.label:
            return u'%s [%s]' % (self.label, self.configuration_string, )
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
        Return a unicode string that represents the configuration for the
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
            return u'%s [%s]' % (self.label, self.configuration_string, )
        else:
            return self.configuration_string


class FallbackSegmentPluginModel(SegmentBasePluginModel):

    @property
    def configuration_string(self):
        return u'Always active'


class SwitchSegmentPluginModel(SegmentBasePluginModel):

    on_off = models.BooleanField(_('Always on?'),
        default=True,
        help_text=_('Uncheck to always hide child plugins.'),
    )

    @property
    def configuration_string(self):
        if self.on_off:
            return u'Always ON'
        else:
            return u'Always OFF'


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
        default='*',
        help_text=_('Name of cookie to consider.'),
        max_length=4096,
    )

    cookie_value = models.CharField(_('value to compare'),
        blank=False,
        default='*',
        help_text=_('Value to consider.'),
        max_length=4096,
    )

    @property
    def configuration_string(self):
        return u'“%s” equals “%s”' % (self.cookie_key, self.cookie_value, )


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
    COUNTRY_CODES = [
        (u'A1', u'Anonymous Proxy'),
        (u'A2', u'Satellite Provider'),
        (u'O1', u'Other Country'),
        (u'AD', u'Andorra'),
        (u'AE', u'United Arab Emirates'),
        (u'AF', u'Afghanistan'),
        (u'AG', u'Antigua and Barbuda'),
        (u'AI', u'Anguilla'),
        (u'AL', u'Albania'),
        (u'AM', u'Armenia'),
        (u'AO', u'Angola'),
        (u'AP', u'Asia/Pacific Region'),
        (u'AQ', u'Antarctica'),
        (u'AR', u'Argentina'),
        (u'AS', u'American Samoa'),
        (u'AT', u'Austria'),
        (u'AU', u'Australia'),
        (u'AW', u'Aruba'),
        (u'AX', u'Aland Islands'),
        (u'AZ', u'Azerbaijan'),
        (u'BA', u'Bosnia and Herzegovina'),
        (u'BB', u'Barbados'),
        (u'BD', u'Bangladesh'),
        (u'BE', u'Belgium'),
        (u'BF', u'Burkina Faso'),
        (u'BG', u'Bulgaria'),
        (u'BH', u'Bahrain'),
        (u'BI', u'Burundi'),
        (u'BJ', u'Benin'),
        (u'BL', u'Saint Bartelemey'),
        (u'BM', u'Bermuda'),
        (u'BN', u'Brunei Darussalam'),
        (u'BO', u'Bolivia'),
        (u'BQ', u'Bonaire, Saint Eustatius and Saba'),
        (u'BR', u'Brazil'),
        (u'BS', u'Bahamas'),
        (u'BT', u'Bhutan'),
        (u'BV', u'Bouvet Island'),
        (u'BW', u'Botswana'),
        (u'BY', u'Belarus'),
        (u'BZ', u'Belize'),
        (u'CA', u'Canada'),
        (u'CC', u'Cocos (Keeling) Islands'),
        (u'CD', u'Congo, The Democratic Republic of the'),
        (u'CF', u'Central African Republic'),
        (u'CG', u'Congo'),
        (u'CH', u'Switzerland'),
        (u'CI', u'Cote d’Ivoire'),
        (u'CK', u'Cook Islands'),
        (u'CL', u'Chile'),
        (u'CM', u'Cameroon'),
        (u'CN', u'China'),
        (u'CO', u'Colombia'),
        (u'CR', u'Costa Rica'),
        (u'CU', u'Cuba'),
        (u'CV', u'Cape Verde'),
        (u'CW', u'Curacao'),
        (u'CX', u'Christmas Island'),
        (u'CY', u'Cyprus'),
        (u'CZ', u'Czech Republic'),
        (u'DE', u'Germany'),
        (u'DJ', u'Djibouti'),
        (u'DK', u'Denmark'),
        (u'DM', u'Dominica'),
        (u'DO', u'Dominican Republic'),
        (u'DZ', u'Algeria'),
        (u'EC', u'Ecuador'),
        (u'EE', u'Estonia'),
        (u'EG', u'Egypt'),
        (u'EH', u'Western Sahara'),
        (u'ER', u'Eritrea'),
        (u'ES', u'Spain'),
        (u'ET', u'Ethiopia'),
        (u'EU', u'Europe'),
        (u'FI', u'Finland'),
        (u'FJ', u'Fiji'),
        (u'FK', u'Falkland Islands (Malvinas)'),
        (u'FM', u'Micronesia, Federated States of'),
        (u'FO', u'Faroe Islands'),
        (u'FR', u'France'),
        (u'GA', u'Gabon'),
        (u'GB', u'United Kingdom'),
        (u'GD', u'Grenada'),
        (u'GE', u'Georgia'),
        (u'GF', u'French Guiana'),
        (u'GG', u'Guernsey'),
        (u'GH', u'Ghana'),
        (u'GI', u'Gibraltar'),
        (u'GL', u'Greenland'),
        (u'GM', u'Gambia'),
        (u'GN', u'Guinea'),
        (u'GP', u'Guadeloupe'),
        (u'GQ', u'Equatorial Guinea'),
        (u'GR', u'Greece'),
        (u'GS', u'South Georgia and the South Sandwich Islands'),
        (u'GT', u'Guatemala'),
        (u'GU', u'Guam'),
        (u'GW', u'Guinea-Bissau'),
        (u'GY', u'Guyana'),
        (u'HK', u'Hong Kong'),
        (u'HM', u'Heard Island and McDonald Islands'),
        (u'HN', u'Honduras'),
        (u'HR', u'Croatia'),
        (u'HT', u'Haiti'),
        (u'HU', u'Hungary'),
        (u'ID', u'Indonesia'),
        (u'IE', u'Ireland'),
        (u'IL', u'Israel'),
        (u'IM', u'Isle of Man'),
        (u'IN', u'India'),
        (u'IO', u'British Indian Ocean Territory'),
        (u'IQ', u'Iraq'),
        (u'IR', u'Iran, Islamic Republic of'),
        (u'IS', u'Iceland'),
        (u'IT', u'Italy'),
        (u'JE', u'Jersey'),
        (u'JM', u'Jamaica'),
        (u'JO', u'Jordan'),
        (u'JP', u'Japan'),
        (u'KE', u'Kenya'),
        (u'KG', u'Kyrgyzstan'),
        (u'KH', u'Cambodia'),
        (u'KI', u'Kiribati'),
        (u'KM', u'Comoros'),
        (u'KN', u'Saint Kitts and Nevis'),
        (u'KP', u'Korea, Democratic People’s Republic of'),
        (u'KR', u'Korea, Republic of'),
        (u'KW', u'Kuwait'),
        (u'KY', u'Cayman Islands'),
        (u'KZ', u'Kazakhstan'),
        (u'LA', u'Lao, People’s Democratic Republic of'),
        (u'LB', u'Lebanon'),
        (u'LC', u'Saint Lucia'),
        (u'LI', u'Liechtenstein'),
        (u'LK', u'Sri Lanka'),
        (u'LR', u'Liberia'),
        (u'LS', u'Lesotho'),
        (u'LT', u'Lithuania'),
        (u'LU', u'Luxembourg'),
        (u'LV', u'Latvia'),
        (u'LY', u'Libyan Arab Jamahiriya'),
        (u'MA', u'Morocco'),
        (u'MC', u'Monaco'),
        (u'MD', u'Moldova, Republic of'),
        (u'ME', u'Montenegro'),
        (u'MF', u'Saint Martin'),
        (u'MG', u'Madagascar'),
        (u'MH', u'Marshall Islands'),
        (u'MK', u'Macedonia'),
        (u'ML', u'Mali'),
        (u'MM', u'Myanmar'),
        (u'MN', u'Mongolia'),
        (u'MO', u'Macao'),
        (u'MP', u'Northern Mariana Islands'),
        (u'MQ', u'Martinique'),
        (u'MR', u'Mauritania'),
        (u'MS', u'Montserrat'),
        (u'MT', u'Malta'),
        (u'MU', u'Mauritius'),
        (u'MV', u'Maldives'),
        (u'MW', u'Malawi'),
        (u'MX', u'Mexico'),
        (u'MY', u'Malaysia'),
        (u'MZ', u'Mozambique'),
        (u'NA', u'Namibia'),
        (u'NC', u'New Caledonia'),
        (u'NE', u'Niger'),
        (u'NF', u'Norfolk Island'),
        (u'NG', u'Nigeria'),
        (u'NI', u'Nicaragua'),
        (u'NL', u'Netherlands'),
        (u'NO', u'Norway'),
        (u'NP', u'Nepal'),
        (u'NR', u'Nauru'),
        (u'NU', u'Niue'),
        (u'NZ', u'New Zealand'),
        (u'OM', u'Oman'),
        (u'PA', u'Panama'),
        (u'PE', u'Peru'),
        (u'PF', u'French Polynesia'),
        (u'PG', u'Papua New Guinea'),
        (u'PH', u'Philippines'),
        (u'PK', u'Pakistan'),
        (u'PL', u'Poland'),
        (u'PM', u'Saint Pierre and Miquelon'),
        (u'PN', u'Pitcairn'),
        (u'PR', u'Puerto Rico'),
        (u'PS', u'Palestinian Territory'),
        (u'PT', u'Portugal'),
        (u'PW', u'Palau'),
        (u'PY', u'Paraguay'),
        (u'QA', u'Qatar'),
        (u'RE', u'Reunion'),
        (u'RO', u'Romania'),
        (u'RS', u'Serbia'),
        (u'RU', u'Russian Federation'),
        (u'RW', u'Rwanda'),
        (u'SA', u'Saudi Arabia'),
        (u'SB', u'Solomon Islands'),
        (u'SC', u'Seychelles'),
        (u'SD', u'Sudan'),
        (u'SE', u'Sweden'),
        (u'SG', u'Singapore'),
        (u'SH', u'Saint Helena'),
        (u'SI', u'Slovenia'),
        (u'SJ', u'Svalbard and Jan Mayen'),
        (u'SK', u'Slovakia'),
        (u'SL', u'Sierra Leone'),
        (u'SM', u'San Marino'),
        (u'SN', u'Senegal'),
        (u'SO', u'Somalia'),
        (u'SR', u'Suriname'),
        (u'SS', u'South Sudan'),
        (u'ST', u'Sao Tome and Principe'),
        (u'SV', u'El Salvador'),
        (u'SX', u'Sint Maarten'),
        (u'SY', u'Syrian Arab Republic'),
        (u'SZ', u'Swaziland'),
        (u'TC', u'Turks and Caicos Islands'),
        (u'TD', u'Chad'),
        (u'TF', u'French Southern Territories'),
        (u'TG', u'Togo'),
        (u'TH', u'Thailand'),
        (u'TJ', u'Tajikistan'),
        (u'TK', u'Tokelau'),
        (u'TL', u'Timor-Leste'),
        (u'TM', u'Turkmenistan'),
        (u'TN', u'Tunisia'),
        (u'TO', u'Tonga'),
        (u'TR', u'Turkey'),
        (u'TT', u'Trinidad and Tobago'),
        (u'TV', u'Tuvalu'),
        (u'TW', u'Taiwan'),
        (u'TZ', u'Tanzania, United Republic of'),
        (u'UA', u'Ukraine'),
        (u'UG', u'Uganda'),
        (u'UM', u'United States Minor Outlying Islands'),
        (u'US', u'United States'),
        (u'UY', u'Uruguay'),
        (u'UZ', u'Uzbekistan'),
        (u'VA', u'Holy See (Vatican City State)'),
        (u'VC', u'Saint Vincent and the Grenadines'),
        (u'VE', u'Venezuela'),
        (u'VG', u'Virgin Islands, British'),
        (u'VI', u'Virgin Islands, U.S.'),
        (u'VN', u'Vietnam'),
        (u'VU', u'Vanuatu'),
        (u'WF', u'Wallis and Futuna'),
        (u'WS', u'Samoa'),
        (u'YE', u'Yemen'),
        (u'YT', u'Mayotte'),
        (u'ZA', u'South Africa'),
        (u'ZM', u'Zambia'),
        (u'ZW', u'Zimbabwe'),
    ]

    # Just sort the list alphabetically by country name
    COUNTRY_CODES.sort(key=itemgetter(1))

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
        return u'%s (%s)' % (self.country_code_names[self.country_code], self.country_code)


class AuthenticatedSegmentPluginModel(SegmentBasePluginModel):

    @property
    def configuration_string(self):
        return u'Is Authenticated'


class Segment(models.Model):
    '''
    This is a hollow, unmanaged model that simply allows us to attach custom
    admin views into the AdminSite.
    '''

    class Meta:
        managed=False
