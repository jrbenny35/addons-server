import random

from rest_framework import serializers

from olympia.amo.tests import user_factory, addon_factory
from olympia import amo
from olympia.addons.forms import icons
from olympia.addons.models import AddonUser, Preview
from olympia.addons.utils import generate_addon_guid
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


class GenerateAddonsSerializer(serializers.Serializer):
    count = serializers.IntegerField(default=10)

    def create_addons(self):
        for _ in range(10):
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
                name=u'Ui-Addon',
                public_stats=True,
                slug='ui-test-2',
                summary=u'My Addon summary',
                tags=['some_tag', 'another_tag', 'ui-testing',
                      'selenium', 'python'],
                total_reviews=777,
                weekly_downloads=22233879,
                developer_comments='This is a testing addon.',
            )
            Preview.objects.create(addon=addon, position=1)
            Review.objects.create(addon=addon, rating=5, user=user_factory())
            Review.objects.create(addon=addon, rating=3, user=user_factory())
            addon.reload()

            addon.save()
            print(
                'Created addon {0} for testing successfully'
                .format(addon.name))

    def create_addon(self):
        default_icons = [x[0] for x in icons() if x[0].startswith('icon/')]
        addon = addon_factory(
            status=STATUS_PUBLIC,
            type=ADDON_EXTENSION,
            average_daily_users=10000,
            users=[UserProfile.objects.get(username='uitest')],
            average_rating=5,
            description=u'My Addon description',
            file_kw={
                'hash': 'fakehash',
                'platform': amo.PLATFORM_ALL.id,
                'size': 42,
            },
            guid=generate_addon_guid(),
            icon_type=random.choice(default_icons),
            name=u'Ui-Addon-Test',
            public_stats=True,
            slug='ui-test-2',
            summary=u'My Addon summary',
            tags=['some_tag', 'another_tag', 'ui-testing',
                  'selenium', 'python'],
            total_reviews=1000,
            weekly_downloads=9999999,
            developer_comments='This is a testing addon.',
        )
        Preview.objects.create(addon=addon, position=1)
        Review.objects.create(addon=addon, rating=5, user=user_factory())
        Review.objects.create(addon=addon, rating=3, user=user_factory())
        addon.reload()

        addon.save()
        print(
            'Created addon {0} for testing successfully'
            .format(addon.name))


    def create_theme(self):
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
        generate_collection(
            addon,
            app=FIREFOX,
            type=amo.COLLECTION_FEATURED)
        # generate_collection(addon, app=FIREFOX,
        #                    author=UserProfile.objects.get(username='uitest'))
        print('Created Theme {0} for testing successfully'.format(addon.name))

    def create_collections(self):
        for _ in range(4):
            addon = addon_factory(type=amo.ADDON_EXTENSION)
            generate_collection(
                addon, APPS['firefox'], type=amo.COLLECTION_FEATURED)

    def create_themes(self):
        owner = UserProfile.objects.get(username='uitest')
        generate_themes(6, owner)
        for _ in range(6):
            addon = addon_factory(status=STATUS_PUBLIC, type=ADDON_PERSONA)
            generate_collection(addon, app=FIREFOX)
