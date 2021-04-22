import logging
import os
import sys
from base64 import b64encode
from datetime import date

from django.conf import settings
from django.db import IntegrityError
from django.urls import reverse

import requests
import xmltodict
from furl import furl

from users.models import Inscription, User

logger = logging.getLogger(__name__)


class IntranetError(Exception):
    pass


class NetidBackend:
    ULB_AUTH = "https://auth-pp.ulb.be/proxyValidate?ticket={}&service={}}/{}"

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, ticket=None):
        if not ticket:
            return None

        resp = requests.get(self.ULB_AUTH.format(ticket, settings.BASE_URL, reverse('auth-ulb')))
        resp.encoding = (
            "utf-8"  # force utf-8 because ulb does not send the right header
        )

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
                email=user_dict["mail"],
                first_name=user_dict["first_name"],
                last_name=user_dict["last_name"],
                registration=user_dict["raw_matricule"],
            )

        return user

    def _parse_response(self, xml):
        if xml.strip() == "":
            raise IntranetError("Empty response")
        if "errMsgFr" in xml:
            raise IntranetError("Response was an error")

        doc = xmltodict.parse(xml)
        user = {}

        user["netid"] = doc["cas:serviceResponse"]["cas:authenticationSuccess"][
            "cas:user"
        ]

        return user

    @classmethod
    def login_url(cls):
        return_url = furl(settings.BASE_URL)
        return_url.path = reverse("auth-ulb")

        ulb_url = furl("https://auth-pp.ulb.be/login")
        ulb_url.args["service"] = return_url

        return ulb_url
