# -*- coding: utf-8 -*-

import logging

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


    def get_country_code(self, ipa):
        if self.geo_ip:
            try:
                return self.geo_ip.country(ipa)['country_code'].upper()
            except:
                pass
        return None


    def process_request(self, request):
        ipa = request.META.get("HTTP_X_FORWARDED_FOR", request.META["REMOTE_ADDR"])
        request.META['COUNTRY_CODE'] = self.get_country_code(ipa)
