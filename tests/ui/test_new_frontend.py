from pages.desktop.home import Home


def test_login(my_base_url, selenium):
    """User can login"""
    selenium.get(my_base_url)
    assert 'Add-ons for Firefox' in selenium.title
