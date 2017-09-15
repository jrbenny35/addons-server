import datetime
import json
import os
import random
import urlparse
from subprocess import call

import jwt
import pytest
import requests
from django.core.management import call_command
from django.conf import settings
from fxapom.fxapom import DEV_URL, PROD_URL, FxATestAccount
from olympia import amo
from olympia.amo.tests import (
    create_switch,
)

# TODO: Change imports to allow running tests against deployed instances.


@pytest.fixture(scope='session')
def my_base_url(base_url, request, pytestconfig, jwt_token):
    """Base URL used to start the 'live_server'."""
    if base_url:
        pytestconfig.option.usingliveserver = False
        return base_url
    else:
        return request.getfixturevalue("live_server").url


@pytest.fixture(scope='session')
def initial_data(base_url, jwt_token):
    """Fixture used to fill database will dummy addons.

    Creates exactly 10 random addons with users that are also randomly
    generated.
    """
    headers = {'Authorization': 'JWT {token}'.format(token=jwt_token)}

    url = '{base_url}/api/v3/landfill/generate-addons/'.format(
        base_url=base_url)

    response = requests.post(
        url,
        data={'count': 10},
        headers=headers)


@pytest.fixture
def capabilities(capabilities):
    # In order to run these tests in Firefox 48, marionette is required
    capabilities['marionette'] = True
    return capabilities


@pytest.fixture
def fxa_account(my_base_url):
    """Account used to login to the AMO site."""
    url = DEV_URL if 'dev' or 'localhost' in my_base_url else PROD_URL
    return FxATestAccount(url)


@pytest.fixture(scope='session')
def jwt_issuer(base_url, variables):
    """JWT Issuer from variables file or env variable named 'JWT_ISSUER'"""
    try:
        hostname = urlparse.urlsplit(base_url).hostname
        return variables['api'][hostname]['jwt_issuer']
    except KeyError:
        return os.getenv('JWT_ISSUER')


@pytest.fixture(scope='session')
def jwt_secret(base_url, variables):
    """JWT Secret from variables file or env vatiable named "JWT_SECRET"""
    try:
        hostname = urlparse.urlsplit(base_url).hostname
        return variables['api'][hostname]['jwt_secret']
    except KeyError:
        return os.getenv('JWT_SECRET')


@pytest.fixture
def create_superuser(my_base_url, transactional_db, tmpdir, variables):
    """Creates a superuser."""
    create_switch('super-create-accounts')
    call_command('loaddata', 'initial.json')
    call_command(
        'createsuperuser',
        interactive=False,
        username='uitest',
        email='uitester@mozilla.org',
        add_to_supercreate_group=True,
        save_api_credentials=str(tmpdir.join('variables.json')),
        hostname=urlparse.urlsplit(my_base_url).hostname
    )
    with tmpdir.join('variables.json').open() as f:
        variables.update(json.load(f))
    print(variables)


@pytest.fixture
def user(create_superuser, my_base_url, fxa_account, jwt_token):
    """This creates a user for logging into the AMO site."""
    url = '{base_url}/api/v3/accounts/super-create/'.format(
        base_url=my_base_url)

    params = {
        'email': fxa_account.email,
        'password': fxa_account.password,
        'username': fxa_account.email.split('@')[0]}
    headers = {'Authorization': 'JWT {token}'.format(token=jwt_token)}
    response = requests.post(url, data=params, headers=headers)
    assert requests.codes.created == response.status_code
    params.update(response.json())
    return params


@pytest.fixture(scope='session')
def jwt_token(jwt_issuer, jwt_secret):
    """This creates a JWT Token"""
    payload = {
        'iss': jwt_issuer,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)}
    print(payload)
    return jwt.encode(payload, jwt_secret, algorithm='HS256')


def pytest_configure(config):
    from olympia.amo.tests import prefix_indexes

    prefix_indexes(config)


@pytest.fixture(scope='session')
def es_test(pytestconfig):
    from olympia.amo.tests import (
        start_es_mocks, stop_es_mocks, amo_search, setup_es_test_data)

    stop_es_mocks()

    es = amo_search.get_es(timeout=settings.ES_TIMEOUT)
    _SEARCH_ANALYZER_MAP = amo.SEARCH_ANALYZER_MAP
    amo.SEARCH_ANALYZER_MAP = {
        'english': ['en-us'],
        'spanish': ['es'],
    }

    setup_es_test_data(es)

    yield

    amo.SEARCH_ANALYZER_MAP = _SEARCH_ANALYZER_MAP
    start_es_mocks()
