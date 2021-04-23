import logging

from django.conf import settings
from django.urls import reverse

import requests
import xmltodict
from furl import furl

from users.models import User

logger = logging.getLogger(__name__)


class IntranetError(Exception):
    pass


class UlbCasBackend:
    CAS_ENDPOINT = "https://auth-pp.ulb.be/"
    LOGIN_METHOD = 'ulb-cas'

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, ticket=None):
        if not ticket:
            return None

        cas_ticket_url = furl(self.CAS_ENDPOINT)
        cas_ticket_url.path = "/proxyValidate"
        cas_ticket_url.args['ticket'] = ticket
        cas_ticket_url.args['service'] = self.get_service_url()

        resp = requests.get(cas_ticket_url.url)

        if not resp.ok:
            logger.error(
                f"ULB bakcend responded with error {resp.status_code}: %s", resp
            )
            return None

        try:
            user_dict = self._parse_response(resp.text)
        except:
            logger.exception("Error while parsing ULB response")
            return None

        try:
            user = User.objects.get(netid=user_dict["netid"])
        except User.DoesNotExist:
            user = User.objects.create_user(
                netid=user_dict["netid"],

                email=user_dict["netid"] + "@ulb.ac.be", # TODO real
                first_name=user_dict["netid"], # TODO real
                last_name=user_dict["netid"], # TODO real

                register_method=self.LOGIN_METHOD,
            )
        user.last_login_method = self.LOGIN_METHOD
        user.save()

        return user

    def _parse_response(self, xml):
        print(xml) # TODO remove

        doc = xmltodict.parse(xml)
        user = {}

        user["netid"] = doc["cas:serviceResponse"]["cas:authenticationSuccess"][
            "cas:user"
        ]

        return user

    @classmethod
    def get_login_url(cls):
        url = furl("https://auth-pp.ulb.be/login")
        url.args["service"] = cls.get_service_url()

        return url.url

    @classmethod
    def get_service_url(cls):
        url = furl(settings.BASE_URL)
        url.path = reverse('auth-ulb')
        return url.url
