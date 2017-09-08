from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.utils import translation

from olympia.landfill.serializers import GenerateAddonsSerializer


class Command(BaseCommand):

    # def add_arguments(self, parser):
    #    """Handle command arguments."""
    #    parser.add_argument('num', type=int)
    #    parser.add_argument(
    #        '--owner', action='store', dest='email',
    #        default='nobody@mozilla.org',
    #        help="Specific owner's email to be created.")
    #    parser.add_argument(
    #        '--app', action='store', dest='app_name',
    #        default='firefox',
    #        help="Specific application targeted by add-ons creation.")

    def handle(self, *args, **kwargs):
        translation.activate('en-US')

        serializer = GenerateAddonsSerializer()
        serializer.create_addons()
        serializer.create_addon()
        serializer.create_theme()
        serializer.create_collections()
        serializer.create_themes()
        cache.clear()
        call_command('clear_cache')
