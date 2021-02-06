import os
import sys
from base64 import b64encode
from datetime import date

from django.conf import settings
from django.db import IntegrityError

import requests
import xmltodict
from furl import furl

from users.models import Inscription, User


class IntranetError(Exception):
    pass


class NetidBackend:
    ULB_AUTH = 'https://www.ulb.ac.be/commons/check?_type=normal&_sid={}&_uid={}'

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, sid=None, uid=None):
        if not (sid and uid):
            return None

        resp = requests.get(self.ULB_AUTH.format(sid, uid))
        resp.encoding = 'utf-8' # force utf-8 because ulb does not send the right header

        try:
            if not os.path.exists("/tmp/netids/"):
                os.mkdir("/tmp/netids/")
            with open(f"/tmp/netids/{sid}__{uid}", "w") as f:
                if sys.version_info.major >= 3:
                    f.write(resp.text)
                else:
                    f.write(resp.text.encode('utf-8'))
        except OSError:
            pass
        except UnicodeEncodeError:
            pass

        if not resp.ok:
            return None

        try:
            user_dict = self._parse_response(resp.text)
        except:
            return None

        try:
            user = User.objects.get(netid=user_dict['netid'])
        except User.DoesNotExist:
            user = User.objects.create_user(
                netid=user_dict['netid'],
                email=user_dict['mail'],
                first_name=user_dict['first_name'],
                last_name=user_dict['last_name'],
                registration=user_dict['raw_matricule'],
            )

        for inscription in user_dict.get('inscriptions', []):
            try:
                year = int(inscription['year'])
            except ValueError:
                continue
            try:
                Inscription.objects.create(
                    user=user,
                    faculty=inscription['fac'],
                    section=inscription['slug'],
                    year=year,
                )
            except IntegrityError:
                pass

        return user

    def _parse_response(self, xml):
        if xml.strip() == '':
            raise IntranetError("Empty response")
        if 'errMsgFr' in xml:
            raise IntranetError('Response was an error')

        doc = xmltodict.parse(xml)
        user = {}

        user['netid'] = doc['intranet']['session']['user']['username']

        identities = doc['intranet']['session']['user']['identity']
        if isinstance(identities, list):
            for identity in identities:
                if identity['email'] is not None:
                    break
        else:
            identity = identities

        user['last_name'] = identity['nom'].title()
        user['first_name'] = identity['prenom']
        user['mail'] = identity['email']

        user['raw_matricule'] = identity['matricule']
        user['matricule'] = user['raw_matricule'].split(":")[-1]

        if user['mail'] is None:
            user['mail'] = user['netid'] + "@ulb.ac.be"
            return user

        user['mail'] = user['mail'].lower()
        user['biblio'] = identity['biblio']

        birthday = identity['dateNaissance']
        user['birthday'] = date(*reversed(list(map(lambda x: int(x), birthday.split('/')))))

        user['inscriptions'] = []

        if identity['inscriptions'] is not None:
            if not isinstance(identity['inscriptions']['inscription'], list):
                inscriptions = [identity['inscriptions']['inscription']]
            else:
                inscriptions = identity['inscriptions']['inscription']

            for inscription in inscriptions:
                user['inscriptions'].append({
                    'year': inscription['anac'],
                    'slug': inscription['anet'],
                    'fac': inscription['facid'],
                })

        return user

    @classmethod
    def login_url(cls, next_url=""):
        return_url = furl(settings.BASE_URL)
        return_url.path = "auth"
        if next_url:
            return_url.args['next64'] = b64encode(next_url.encode()).decode()

        ulb_url = furl("https://www.ulb.ac.be/commons/intranet")
        ulb_url.args["_prt"] = "ulb:gehol"
        ulb_url.args["_ssl"] = "on"
        ulb_url.args["_prtm"] = "redirect"
        ulb_url.args["_appl"] = return_url

        return ulb_url
