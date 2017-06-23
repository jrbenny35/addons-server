import datetime
import json
import os
import random
import string
import urlparse

import jwt
import pytest
import requests
from django.core.management import call_command
from fxapom.fxapom import DEV_URL, PROD_URL, FxATestAccount
from olympia import amo
from olympia.addons.forms import icons
from olympia.addons.models import AddonUser, Preview
from olympia.addons.utils import generate_addon_guid
from olympia.amo.tests import (
    addon_factory,
    create_switch,
    user_factory,
    version_factory,
)
from olympia.constants.applications import APPS, FIREFOX
from olympia.constants.base import (
    ADDON_EXTENSION,
    ADDON_PERSONA,
    STATUS_PUBLIC
)
from olympia.landfill.collection import generate_collection
from olympia.landfill.generators import generate_themes
from olympia.reviews.models import Review
from olympia.users.models import UserProfile
from pytest_django import live_server_helper

# TODO: Change imports to allow running tests against deployed instances.


@pytest.fixture(scope='function')
def my_base_url(base_url, request, pytestconfig):
    """Base URL used to start the 'live_server'."""
    if base_url:
        pytestconfig.option.usingliveserver = False
        return base_url
    elif 'mobile-ui-tests' in os.getenv('TOXENV'):
        url = urlparse.urlsplit(request.getfixturevalue("live_server").url)
        return 'olympia.dev:{0}'.format(url.port)
    else:
        return request.getfixturevalue("live_server").url


@pytest.fixture
def capabilities(capabilities):
    # In order to run these tests in Firefox 48, marionette is required
    capabilities['marionette'] = True
    capabilities['acceptInsecureCerts'] = True

    if os.getenv('TOXENV') == 'mobile-ui-tests':
        capabilities['browserName'] = 'Chrome'
        capabilities['appiumVersion'] = '1.6.4'
        capabilities['deviceName'] = 'Android Emulator'
        capabilities['deviceOrientation'] = 'portrait'
        capabilities['platformVersion'] = '6.0'
        capabilities['platformName'] = 'Android'

    return capabilities


@pytest.fixture
def firefox_options(firefox_options):
    firefox_options.set_preference(
        'extensions.install.requireBuiltInCerts', False)
    firefox_options.set_preference('xpinstall.signatures.required', False)
    firefox_options.set_preference('extensions.webapi.testing', True)
    return firefox_options


@pytest.fixture
def fxa_account(my_base_url):
    """Account used to login to the AMO site."""
    url = DEV_URL if 'dev' or 'localhost' in my_base_url else PROD_URL
    return FxATestAccount(url)


@pytest.fixture()
def jwt_issuer(my_base_url, variables):
    """JWT Issuer from variables file or env variable named 'JWT_ISSUER'"""
    try:
        hostname = urlparse.urlsplit(my_base_url).hostname
        return variables['api'][hostname]['jwt_issuer']
    except KeyError:
        return os.getenv('JWT_ISSUER')


@pytest.fixture()
def jwt_secret(my_base_url, variables):
    """JWT Secret from variables file or env vatiable named "JWT_SECRET"""
    try:
        hostname = urlparse.urlsplit(my_base_url).hostname
        return variables['api'][hostname]['jwt_secret']
    except KeyError:
        return os.getenv('JWT_SECRET')


@pytest.fixture
def initial_data(transactional_db, pytestconfig):
    """Fixture used to fill database will dummy addons.

    Creates exactly 10 random addons with users that are also randomly
    generated.
    """
    if not pytestconfig.option.usingliveserver:
        return

    for _ in range(10):
        AddonUser.objects.create(user=user_factory(), addon=addon_factory())


@pytest.fixture
def theme(transactional_db, create_superuser, pytestconfig):
    """Creates a custom theme named 'Ui-Test Theme'.

    This theme will be a featured theme and will belong to the user created by
    the 'create_superuser' fixture.

    It has one author.
    """
    if not pytestconfig.option.usingliveserver:
        return

    addon = addon_factory(
        status=STATUS_PUBLIC,
        type=ADDON_PERSONA,
        average_daily_users=4242,
        users=[UserProfile.objects.get(username='uitest')],
        average_rating=5,
        description=u'My UI Theme description',
        file_kw={
            'hash': 'fakehash',
            'platform': amo.PLATFORM_ALL.id,
            'size': 42,
        },
        guid=generate_addon_guid(),
        homepage=u'https://www.example.org/',
        name=u'Ui-Test Theme',
        public_stats=True,
        slug='ui-test',
        summary=u'My UI theme summary',
        support_email=u'support@example.org',
        support_url=u'https://support.example.org/support/ui-theme-addon/',
        tags=['some_tag', 'another_tag', 'ui-testing',
                'selenium', 'python'],
        total_reviews=777,
        weekly_downloads=123456,
        developer_comments='This is a testing theme, used within pytest.',
    )
    addon.save()
    generate_collection(addon, app=FIREFOX,
                        author=UserProfile.objects.get(username='uitest'))
    print('Created Theme {0} for testing successfully'.format(addon.name))
    return addon


@pytest.fixture
def addon(transactional_db, create_superuser, pytestconfig):
    """Creates a custom addon named 'Ui-Addon'.

    This addon will be a featured addon and will have a featured collecton
    attatched to it. It will belong to the user created by the
    'create_superuser' fixture.

    It has 1 preview, 5 reviews, and 2 authors. The second author is named
    'ui-tester2'. It has a version number as well as a beta version.
    """
    if not pytestconfig.option.usingliveserver:
        return

    default_icons = [x[0] for x in icons() if x[0].startswith('icon/')]
    addon = addon_factory(
        status=STATUS_PUBLIC,
        type=ADDON_EXTENSION,
        average_daily_users=5567,
        users=[UserProfile.objects.get(username='uitest')],
        average_rating=5,
        description=u'My Addon description',
        file_kw={
            'platform': amo.PLATFORM_ALL.id,
            'size': 42,
        },
        guid='test-desktop@nowhere',
        homepage=u'https://www.example.org/',
        icon_type=random.choice(default_icons),
        name=u'Ui-Addon',
        public_stats=True,
        slug='ui-test',
        summary=u'My Addon summary',
        support_email=u'support@example.org',
        support_url=u'https://support.example.org/support/ui-test-addon/',
        tags=['some_tag', 'another_tag', 'ui-testing',
              'selenium', 'python'],
        total_reviews=888,
        weekly_downloads=2147483647,
        developer_comments='This is a testing addon, used within pytest.',
        is_experimental=True,
    )
    Preview.objects.create(addon=addon, position=1)
    Review.objects.create(addon=addon, rating=5, user=user_factory())
    Review.objects.create(addon=addon, rating=3, user=user_factory())
    Review.objects.create(addon=addon, rating=2, user=user_factory())
    Review.objects.create(addon=addon, rating=1, user=user_factory())
    addon.reload()
    AddonUser.objects.create(user=user_factory(username='ui-tester2'),
                             addon=addon, listed=True)
    version_factory(addon=addon, file_kw={'status': amo.STATUS_BETA},
                    version='1.1beta')
    addon.save()
    generate_collection(addon, app=FIREFOX)
    print('Created addon {0} for testing successfully'.format(addon.name))
    return addon


@pytest.fixture
def minimal_addon(transactional_db, create_superuser, pytestconfig):
    """Creates a custom addon named 'Ui-Addon-2'.

    It will belong to the user created by the 'create_superuser' fixture.

    It has 1 preview, and 2 reviews.
    """
    if not pytestconfig.option.usingliveserver:
        return

    default_icons = [x[0] for x in icons() if x[0].startswith('icon/')]
    addon = addon_factory(
        status=STATUS_PUBLIC,
        type=ADDON_EXTENSION,
        average_daily_users=7000,
        users=[UserProfile.objects.get(username='uitest')],
        average_rating=3,
        description=u'My Addon description',
        file_kw={
            'hash': 'fakehash',
            'platform': amo.PLATFORM_ALL.id,
            'size': 42,
        },
        guid=generate_addon_guid(),
        icon_type=random.choice(default_icons),
        name=u'Ui-Addon-2',
        public_stats=True,
        slug='ui-test-2',
        summary=u'My Addon summary',
        tags=['some_tag', 'another_tag', 'ui-testing',
              'selenium', 'python'],
        total_reviews=777,
        weekly_downloads=22233879,
        developer_comments='This is a testing addon, used within pytest.',
    )
    Preview.objects.create(addon=addon, position=1)
    Review.objects.create(addon=addon, rating=5, user=user_factory())
    Review.objects.create(addon=addon, rating=3, user=user_factory())
    addon.reload()

    addon.save()
    generate_collection(addon, app=FIREFOX)
    print('Created addon {0} for testing successfully'.format(addon.name))
    return addon


@pytest.fixture
def themes(transactional_db, create_superuser, pytestconfig):
    """Creates exactly 6 themes that will be not featured.

    These belong to the user created by the 'create_superuser' fixture.
    It will also create 6 themes that are featured with random authors.
    """
    if not pytestconfig.option.usingliveserver:
        return

    owner = UserProfile.objects.get(username='uitest')
    generate_themes(6, owner)
    for _ in range(6):
        addon = addon_factory(status=STATUS_PUBLIC, type=ADDON_PERSONA)
        generate_collection(addon, app=FIREFOX)


@pytest.fixture
def collections(transactional_db, pytestconfig):
    """Creates exactly 4 collections that are featured.

    This fixture uses the generate_collection function from olympia.
    """
    if not pytestconfig.option.usingliveserver:
        return

    for _ in range(4):
        addon = addon_factory(type=amo.ADDON_EXTENSION)
        generate_collection(
            addon, APPS['firefox'], type=amo.COLLECTION_FEATURED)


@pytest.fixture
def gen_webext(create_superuser, pytestconfig, tmpdir, transactional_db):
    """Creates a a blank webextenxtension."""
    if not pytestconfig.option.usingliveserver:
        return

    from olympia.files.models import File, FileUpload
    from olympia.versions.models import Version
    from olympia.amo.tests.test_helpers import get_addon_file
    from django.utils.translation import activate
    from django.core.files.uploadedfile import SimpleUploadedFile
    import os

    manifest = tmpdir.mkdir('webext').join('manifest.json')
    # print(manifest)
    webext = {
        'applications': {
            'gecko': {
                'id': 'ui-addon@mozilla.org',
            }
        },
        'manifest_version': 2,
        'name': 'Ui-Addon',
        'version': 3.1,
        'description': 'Blank Webextension for testing',
        'permissions': [],
        'background': {
            'scripts': 'background.js',
        }
    }
    activate('en')
    # manifest.write(json.dump(webext, manifest, indent=2))
    # json.dump(webext, manifest, indent=2)
    with open(str(manifest), 'w') as outfile:
        json.dump(webext, outfile, indent=2)
    default_icons = [x[0] for x in icons() if x[0].startswith('icon/')]
    addon = addon_factory(
        status=STATUS_PUBLIC,
        type=ADDON_EXTENSION,
        average_daily_users=5567,
        users=[UserProfile.objects.get(username='uitest')],
        average_rating=5,
        description=u'My Addon description',
        file_kw={
            'hash': 'fakehash',
            'platform': amo.PLATFORM_ALL.id,
            'size': 42,
        },
        guid='firebug@software.joehewitt.com',
        homepage=u'https://www.example.org/',
        icon_type=random.choice(default_icons),
        name=u'Ui-Addon',
        public_stats=True,
        slug='ui-test',
        summary=u'My Addon summary',
        support_email=u'support@example.org',
        support_url=u'https://support.example.org/support/ui-test-addon/',
        tags=['some_tag', 'another_tag', 'ui-testing',
              'selenium', 'python'],
        total_reviews=888,
        weekly_downloads=2147483647,
        developer_comments='This is a testing addon, used within pytest.',
    )
    Preview.objects.create(addon=addon, position=1)
    version = version_factory(addon=addon, file_kw={'status': amo.STATUS_BETA},
                    version='1.1beta')
    addon.reload()
    # zip as .xpi
    # os.system('zip -r {0} {1}'.format(tmpdir.join('webext_comp.xpi'), manifest))
    # return tmpdir.join('webext_comp.xpi').open()
    # print(tmpdir.listdir())
    # with open(str(tmpdir.join('webext_comp.xpi')), 'r') as outfile:
    Version.from_upload(upload=upload, addon=addon, platforms=[amo.PLATFORM_ALL.id], channel=amo.RELEASE_CHANNEL_LISTED)
    addon.save()


@pytest.fixture
def gen_webext2(create_superuser):
    import django
    import mimetypes
    from django.conf import settings

    from olympia.files.models import File, FileUpload
    from olympia.files.tests.test_helpers import get_file
    from django.core.files.uploadedfile import SimpleUploadedFile
    from olympia.editors.helpers import ReviewHelper
    from olympia.users.models import UserProfile
    from olympia.amo.tests import addon_factory, copy_file_to_temp

    addon = addon_factory()
    if settings.CELERY_ALWAYS_EAGER:
        print("IS TRUE")
    user = UserProfile.objects.get(username='uitest')
    user_factory(id=settings.TASK_USER_ID)
    # f = File()
    # upload = FileUpload.objects.create(path=get_file('webextension_no_id.xpi'), hash=f.generate_hash(get_file('webextension_no_id.xpi')))
    # upload = FileUpload.objects.create(path=tmpdir.join('webext_comp.xpi'))
    # Version.from_upload(upload=upload, addon=addon, platforms=[amo.PLATFORM_ALL.id], channel=amo.RELEASE_CHANNEL_LISTED)
    file_to_upload = 'webextension_no_id.xpi'
    file_path = get_file(file_to_upload)

    # make sure we are not using the file in the source-tree but a temporary
    # one to avoid the files get moved somewhere else and deleted from source
    # tree
    with copy_file_to_temp(file_path) as temporary_path:
        data = open(temporary_path).read()
        filedata = SimpleUploadedFile(
            file_to_upload,
            data,
            content_type=mimetypes.guess_type(file_to_upload)[0])

    # now, lets upload the file into the system
    from olympia.devhub.views import handle_upload

    upload = handle_upload(
        filedata=filedata,
        user=user,
        channel=amo.RELEASE_CHANNEL_LISTED,
        addon=addon,
        submit=True
    )

    # find the latest version that we just uploaded (should be version 1.0
    # which is what webextension_no_id.xpi defines)
    latest_version = upload.addon.find_latest_version(amo.RELEASE_CHANNEL_LISTED)

    # now process the add-on and publish it
    helper = ReviewHelper(addon=upload.addon, version=latest_version)
    helper.handler.data = {'comments': ''}
    helper.handler.process_public()


@pytest.fixture
def create_superuser(transactional_db, my_base_url, tmpdir, variables):
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


@pytest.fixture(scope='function')
def live_server(request, transactional_db, pytestconfig):
    """This fixture overrides the live_server fixture provided by pytest_django.

    live_server allows us to create a running version of the
    addons django application within pytest for testing.

    cgrebs:
    From what I found out was that the `live_server` fixture (in our setup,
    couldn't reproduce in a fresh project) apparently starts up the
    LiveServerThread way too early before pytest-django configures the
    settings correctly.

    That resulted in the LiveServerThread querying the 'default' database
    which was different from what the other fixtures and tests were using
    which resulted in the problem that the just created api keys could not
    be found in the api methods in the live-server.

    I worked around that by implementing the live_server fixture ourselfs
    and make it function-scoped so that it now runs in a proper
    database-transaction.

    This is a HACK and I'll work on a more permanent solution but for now
    it should be enough to continue working on porting tests...

    Also investigating if there are any problems in pytest-django directly.
    """

    addr = (request.config.getvalue('liveserver') or
            os.getenv('DJANGO_LIVE_TEST_SERVER_ADDRESS'))

    if not addr:
        addr = 'localhost:8081,8100-8200'

    server = live_server_helper.LiveServer(addr)
    pytestconfig.option.usingliveserver = True
    yield server
    server.stop()


@pytest.fixture
def jwt_token(my_base_url, jwt_issuer, jwt_secret):
    """This creates a JWT Token"""
    payload = {
        'iss': jwt_issuer,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)}
    return jwt.encode(payload, jwt_secret, algorithm='HS256')
