import logging
import xml.etree.ElementTree as ET

from django.conf import settings
from django.urls import reverse

import requests
from furl import furl

from users.models import User

logger = logging.getLogger(__name__)


class UlbCasBackend:
    CAS_ENDPOINT = "https://auth-pp.ulb.be/"
    LOGIN_METHOD = 'ulb-cas'
    XML_NAMESPACES = {
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

        # Craft request to the CAS provider
        cas_ticket_url = furl(self.CAS_ENDPOINT)
        cas_ticket_url.path = "/proxyValidate"
        cas_ticket_url.args['ticket'] = ticket
        cas_ticket_url.args['service'] = self.get_service_url()

        # Send the request
        resp = requests.get(cas_ticket_url.url)

        if not resp.ok:
            raise CasRequestError(resp)

        user_dict = self._parse_response(resp.text)

        # Get or create a user from the parsed user_dict
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
        # Try to parse the response from the CAS provider
        try:
            tree = ET.fromstring(xml)
        except ET.ParseError:
            raise CasParseError("invalid-xml", xml)

        success = tree.find(
            './cas:authenticationSuccess',
            namespaces=self.XML_NAMESPACES
        )
        if not success:
            failure = tree.find(
                './cas:authenticationFailure',
                namespaces=self.XML_NAMESPACES
            )
            if failure is not None:
                raise CasRejectError(failure.attrib.get('code'), failure.text)
            else:
                raise CasParseError("unknown-structure", xml)

        netid_node = success.find("cas:user", namespaces=self.XML_NAMESPACES)
        if netid_node is not None:
            netid = netid_node.text
        else:
            raise CasParseError("unknown-structure", xml)

        email_node = success.find("./cas:attributes/cas:mail", namespaces=self.XML_NAMESPACES)
        if email_node is not None:
            email = email_node.text
        else:
            email = f'{netid}@ulb.ac.be'

        return {
            'netid': netid,
            'email': email,
        }

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


class CasError(Exception):
    pass


class CasRequestError(CasError):
    pass


class CasParseError(CasError):
    pass


class CasRejectError(CasError):
    pass
