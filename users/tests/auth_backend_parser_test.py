# import pytest

from users.authBackend import NetidBackend
import datetime

parse = NetidBackend()._parse_response


nimarcha = {
    'netid': 'nimarcha',
    'last_name': 'Marchant',
    'first_name': 'Nikita',
    'mail': 'nikita.marchant@ulb.ac.be',
    'biblio': '3186696',
    'birthday': datetime.date(1993, 5, 24),
    'raw_matricule': 'ulb:etudiants:000362588',
    'matricule': '000362588',
}

inscription = {
    'year': '2013',
    'slug': 'DEV-SCIE',
    'fac': 'sciences',
}


def test_parser():
    xml = open("users/tests/xml-fixtures/nimarcha.xml").read()
    ret = parse(xml)

    ret.pop('inscriptions')
    assert ret == nimarcha


def test_parser_inscriptions():
    xml = open("users/tests/xml-fixtures/nimarcha.xml").read()
    ret = parse(xml)

    inscriptions = ret['inscriptions']
    assert type(inscriptions) is list
    assert len(inscriptions) == 4
    assert inscriptions[0] == inscription


def test_parser_single_inscription():
    xml = open("users/tests/xml-fixtures/nimarcha_single.xml").read()
    ret = parse(xml)

    inscriptions = ret['inscriptions']
    assert type(inscriptions) is list
    assert len(inscriptions) == 1
    assert inscriptions[0] == inscription


def test_parser_minimal():
    xml = open("users/tests/xml-fixtures/minimal.xml").read()
    ret = parse(xml)

    ret.pop('inscriptions')
    assert ret == nimarcha


def test_parser_vub():
    xml = open("users/tests/xml-fixtures/vub.xml").read()
    ret = parse(xml)

    assert ret['last_name'] == "Doe"
    assert ret['first_name'] == "John"
    assert ret['mail'] == "testnetid@ulb.ac.be"
    assert 'inscriptions' not in ret.keys()
