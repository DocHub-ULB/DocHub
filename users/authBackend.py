import logging
import xml.etree.ElementTree as ET

from django.conf import settings
from django.urls import reverse

import requests
from furl import furl

from users.models import User

logger = logging.getLogger(__name__)


class IntranetError(Exception):
    pass


class UlbCasBackend:
    CAS_ENDPOINT = "https://auth-pp.ulb.be/"
    LOGIN_METHOD = 'ulb-cas'
    NAMESPACES = {
        'cas': 'http://www.yale.edu/tp/cas',
    }

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
            raise # TODO : show error to user

        try:
            user_dict = self._parse_response(resp.text)
        except:
            raise # TODO : show error to user

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

        doc = ET.fromstring(xml)
        user = {
            'netid': self._get_tag(doc, './cas:authenticationSuccess/cas:user'),
            'email': self._get_tag(doc, './cas:authenticationSuccess/cas:mail'),
        }

        return user

    def _get_tag(self, tree, xpath):
        node = tree.find(xpath, namespaces=self.NAMESPACES)
        if node is not None:
            return node.text
        else:
            return None

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
