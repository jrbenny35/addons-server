from subprocess import call

import pytest

from pages.desktop.home import Home


# @pytest.fixture(autouse=True)
# def refresh_cache():#
#    call({'python manage.py clear_cache'}, shell=True)
    # Home(selenium, my_base_url).open()
    # call({'echo flush_all > $MEMCACHE_LOCATION'}, shell=True)
    # Home(selenium, my_base_url).open()
    # call({'echo flush_all > $MEMCACHE_LOCATION'}, shell=True)


@pytest.mark.nondestructive
def test_there_are_ten_most_popular_extensions(
        my_base_url, selenium):
    """Ten most popular add-ons are listed"""
    page = Home(selenium, my_base_url).open()
    assert len(page.most_popular.extensions) == 10


@pytest.mark.nondestructive
def test_most_popular_extensions_are_sorted_by_users(
        my_base_url, selenium):
    """Most popular add-ons are sorted by popularity"""
    page = Home(selenium, my_base_url).open()
    extensions_page = page.most_popular.extensions
    sorted_by_users = sorted(extensions_page,
                             key=lambda e: e.users, reverse=True)
    assert sorted_by_users == extensions_page


@pytest.mark.smoke
@pytest.mark.nondestructive
def test_that_clicking_on_addon_name_loads_details_page(
        my_base_url, selenium):
    """Details page addon name matches clicked addon"""
    page = Home(selenium, my_base_url).open()
    name = page.featured_extensions.extensions[0].name
    extension_page = page.featured_extensions.extensions[0].see_all()
    assert name in extension_page.description_header.name


@pytest.mark.smoke
@pytest.mark.nondestructive
def test_that_featured_themes_exist_on_the_home(
        my_base_url, selenium):
    """Featured themes are displayed"""
    page = Home(selenium, my_base_url).open()
    assert len(page.featured_themes.themes) == 6


@pytest.mark.nondestructive
def test_that_clicking_see_all_themes_link_works(
        my_base_url, selenium):
    """Amount of featured themes matches on both pages"""
    page = Home(selenium, my_base_url).open()
    themes = page.featured_themes.themes
    theme_page = page.featured_themes.see_all()
    assert len(themes) == len(theme_page.featured.themes)


@pytest.mark.nondestructive
def test_that_featured_extensions_exist_on_the_home(
        my_base_url, selenium):
    """Featured extensions exist on home page"""
    page = Home(selenium, my_base_url).open()
    assert len(page.featured_extensions.extensions) >= 1


@pytest.mark.nondestructive
def test_that_clicking_see_all_collections_link_works(
        my_base_url, selenium):
    """Amount of featured themes matches on both pages"""
    page = Home(selenium, my_base_url).open()
    collections = page.featured_collections.collections
    collections_page = page.featured_collections.see_all()
    assert len(collections) == len(collections_page.collections)
