# -*- coding: utf-8 -*-

import logging

# from django.contrib.gis.utils import GeoIP
from django.contrib.gis.geoip import GeoIP

logger = logging.getLogger(__name__)


class ResolveCountryCodeMiddleware(object):

    '''
    This middleware uses the GeoIP API to resolve country codes from the
    visitors IP Address.
    '''

    #
    # Initialize the GeoIP DB API. This is only done once, and it happens on
    # the first request.
    #

    try:
        geo_ip = GeoIP()
        logger.info('GeoIP initialized and middleware installed.')
    except:
        geo_ip = False
        logger.critical('Could not initialize GeoIP.')


    @classmethod
    def get_country_code(cls, ipa):
        if cls.geo_ip:
            try:
                return cls.geo_ip.country(ipa)['country_code'].upper()
            except:
                pass
        return None


    @classmethod
    def process_request(cls, request):
        ipa = request.META.get("HTTP_X_FORWARDED_FOR", request.META["REMOTE_ADDR"])
        request.META['COUNTRY_CODE'] = cls.get_country_code(ipa)
