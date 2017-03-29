# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import re
import pytest

from pages.desktop.details import Details


class TestDetails:

    @pytest.mark.nondestructive
    def test_that_register_login_link_is_present_in_addon_details_page(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert details_page.header.is_register_link_visible, 'Register link is not visible'
        assert details_page.header.is_login_link_visible, 'Login links is not visible'

    @pytest.mark.action_chains
    @pytest.mark.nondestructive
    def test_that_dropdown_menu_is_present_after_click_on_other_apps(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert 'Other Applications' == details_page.header.menu_name
        details_page.header.hover_over_other_apps_menu()
        assert details_page.header.is_other_apps_dropdown_menu_visible

    @pytest.mark.nondestructive
    def test_that_addon_name_is_displayed(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        # check that the name is not empty
        assert not details_page.title == ''

    @pytest.mark.nondestructive
    def test_that_summary_is_displayed(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        # check that the summary is not empty
        assert re.match('(\w+\s*){3,}', details_page.summary) is not None

    @pytest.mark.nondestructive
    def test_that_about_this_addon_is_displayed(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert 'About this Add-on' == details_page.about_addon
        assert re.match('(\w+\s*){3,}', details_page.description) is not None

    @pytest.mark.action_chains
    @pytest.mark.nondestructive
    def test_that_version_information_is_displayed(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert 'Version Information' == details_page.version_information_heading

        details_page.expand_version_information()
        assert details_page.is_version_information_section_expanded
        assert details_page.is_source_code_license_information_visible
        assert details_page.is_whats_this_license_visible
        assert details_page.is_view_the_source_link_visible
        assert details_page.is_complete_version_history_visible
        assert details_page.is_version_information_install_button_visible
        # check that the release number matches the version number at the top of the page
        assert 'Version %s' % details_page.version_number == details_page.release_version

    @pytest.mark.smoke
    @pytest.mark.nondestructive
    def test_that_reviews_are_displayed(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert 'Reviews' == details_page.review_title
        assert details_page.has_reviews
        for review in details_page.review_details:
            assert review is not None

    @pytest.mark.nondestructive
    def test_that_tags_are_displayed(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert details_page.are_tags_visible

    @pytest.mark.nondestructive
    def test_part_of_collections_are_displayed(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert 'Part of these Collections' == details_page.part_of_collections_header
        assert len(details_page.part_of_collections) > 0

    @pytest.mark.nondestructive
    def test_that_external_link_leads_to_addon_website(self, my_base_url, selenium, ui_addon):
        # Step 1 - Open AMO Home
        # Step 2 - Open MemChaser Plus details page
        details_page = Details(selenium, my_base_url, "Ui-Test")
        website_link = details_page.website
        assert not website_link == ''
        # Step 3 - Follow external website link
        details_page.click_website_link()
        assert 'www.example.org' in details_page.get_url_current_page()

    @pytest.mark.nondestructive
    def test_that_whats_this_link_for_source_license_links_to_an_answer_in_faq(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        details_page.expand_version_information()
        user_faq_page = details_page.click_whats_this_license()
        assert re.match('(\w+\s*){3,}', user_faq_page.license_question) is not None
        assert re.match('(\w+\s*){3,}', user_faq_page.license_answer) is not None

    @pytest.mark.nondestructive
    def test_author_addons_when_there_are_multiple_authors(self, my_base_url, selenium, ui_addon, ui_addon_2):
        addon_with_multiple_authors = 'Ui-Test'
        page = Details(selenium, my_base_url, addon_with_multiple_authors)
        assert len(page.authors) > 1
        assert 'Other add-ons by these authors' == page.author_addons.heading

    @pytest.mark.nondestructive
    def test_author_addons_when_there_is_only_one_author(self, my_base_url, selenium, ui_addon, ui_addon_2):
        addon_with_one_author = 'Ui-Test-2'
        page = Details(selenium, my_base_url, addon_with_one_author)
        assert len(page.authors) == 1
        assert 'Other add-ons by %s' % page.authors[0] == page.author_addons.heading

    @pytest.mark.nondestructive
    def test_navigating_to_author_addons(self, my_base_url, selenium, ui_addon, ui_addon_2):
        addon_page = Details(selenium, my_base_url, "Ui-Test-2")
        for i in range(len(addon_page.author_addons.addons)):
            author_addon_name = addon_page.author_addons.addons[i].name
            addon_page.author_addons.addons[i].click()
            assert author_addon_name in selenium.title
            selenium.back()

    @pytest.mark.nondestructive
    def test_open_close_functionality_for_image_viewer(self, my_base_url, selenium, ui_addon):
        page = Details(selenium, my_base_url, "Ui-Test")
        viewer = page.previews.thumbnails[0].click()
        assert viewer.is_displayed
        viewer.close()
        assert not viewer.is_displayed

    @pytest.mark.nondestructive
    def test_image_viewer_navigation(self, my_base_url, selenium, ui_addon):
        page = Details(selenium, my_base_url, "Ui-Test")
        thumbnails = page.previews.thumbnails
        viewer = thumbnails[0].click()
        assert viewer.is_previous_disabled
        for i in range(len(thumbnails)):
            assert viewer.images[i].is_displayed
            assert thumbnails[i].title == viewer.caption
            assert thumbnails[i].source.split('/')[-1] == viewer.images[i].source.split('/')[-1]
            viewer.click_next()
        assert viewer.is_next_disabled
        for i in range(len(thumbnails) - 1, -1, -1):
            assert viewer.images[i].is_displayed
            assert thumbnails[i].title == viewer.caption
            assert thumbnails[i].source.split('/')[-1] == viewer.images[i].source.split('/')[-1]
            viewer.click_previous()
        assert viewer.is_previous_disabled

    @pytest.mark.nondestructive
    def test_that_review_usernames_are_clickable(self, my_base_url, selenium, ui_addon):
        addon_name = 'Ui-Test'
        detail_page = Details(selenium, my_base_url, addon_name)

        for i in range(0, len(detail_page.reviews)):
            username = detail_page.reviews[i].username
            amo_user_page = detail_page.reviews[i].click_username()
            assert username == amo_user_page.username
            Details(selenium, my_base_url, addon_name)

    @pytest.mark.nondestructive
    def test_that_clicking_info_link_slides_down_page_to_version_info(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        details_page.click_version_info_link()
        assert details_page.version_info_link == details_page.version_information_href
        assert details_page.is_version_information_section_expanded
        assert details_page.is_version_information_section_in_view

    def test_that_add_a_review_button_works(self, my_base_url, selenium, ui_addon, logged_in):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        selenium.add_cookie(logged_in)
        review_box = details_page.click_to_write_review()
        assert review_box.is_review_box_visible

    @pytest.mark.nondestructive
    def test_the_developers_comments_section(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert u'Developer\u2019s Comments' == details_page.devs_comments_title
        details_page.expand_devs_comments()
        assert details_page.is_devs_comments_section_expanded
        assert re.match('(\w+\s*){3,}', details_page.devs_comments_message) is not None

    @pytest.mark.nondestructive
    def test_that_the_development_channel_expands(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert 'Development Channel' == details_page.development_channel_text
        assert '' == details_page.development_channel_content
        details_page.click_development_channel()
        assert details_page.development_channel_content is not None
        details_page.click_development_channel()
        assert '' == details_page.development_channel_content

    @pytest.mark.nondestructive
    def test_click_on_other_collections(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        for i in range(0, len(details_page.part_of_collections)):
            name = details_page.part_of_collections[i].name
            collection_pg = details_page.part_of_collections[i].click_collection()
            assert name == collection_pg.collection_name, 'Expected collection name does not match the page header'
            details_page = Details(selenium, my_base_url, "Ui-Test")

    @pytest.mark.nondestructive
    def test_the_development_channel_section(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert 'Development Channel' == details_page.development_channel_text
        details_page.click_development_channel()

        # Verify if description present
        assert details_page.development_channel_content is not None
        assert details_page.is_development_channel_install_button_visible

        # Verify experimental version (beta or pre)
        assert details_page.beta_version is not None

    @pytest.mark.nondestructive
    def test_that_license_link_works(self, my_base_url, selenium, ui_addon):
        addon_name = 'Ui-Test'
        details_page = Details(selenium, my_base_url, addon_name)
        assert 'Mozilla Public License, version 2.0' == details_page.license_link_text
        license_link = details_page.license_site
        assert license_link is not None

    @pytest.mark.nondestructive
    def test_that_clicking_user_reviews_slides_down_page_to_reviews_section(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        details_page.click_user_reviews_link()
        assert details_page.is_reviews_section_visible
        assert details_page.is_reviews_section_in_view

    @pytest.mark.action_chains
    @pytest.mark.nondestructive
    def test_that_install_button_is_clickable(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert 'active' in details_page.click_and_hold_install_button_returns_class_value()

    @pytest.mark.nondestructive
    def test_what_is_this_in_the_version_information(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert 'Version Information' == details_page.version_information_heading
        details_page.expand_version_information()
        assert 'What\'s this?' == details_page.license_faq_text
        license_faq = details_page.click_whats_this_license()
        assert 'Frequently Asked Questions' == license_faq.header_text

    @pytest.mark.nondestructive
    def test_view_the_source_in_the_version_information(self, my_base_url, selenium, ui_addon):
        details_page = Details(selenium, my_base_url, "Ui-Test")
        assert 'Version Information' == details_page.version_information_heading
        details_page.expand_version_information()
        assert 'View the source' == details_page.view_source_code_text
        view_source = details_page.click_view_source_code()
        assert '/files/browse/' in details_page.get_url_current_page()
