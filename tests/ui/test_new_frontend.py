from pages.desktop.home import Home


def test_login(my_base_url, selenium):
    """User can login"""
    Home(selenium, my_base_url).open()
    assert 'Add-ons for Firefox' in selenium.title
