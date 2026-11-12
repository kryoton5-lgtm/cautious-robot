"""Simple HTTP contract checks, independent from UI browser state."""
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest


@pytest.mark.http
@pytest.mark.parametrize("path,content_type", [
    ("/", "text/html"), ("/resume.html", "text/html"),
    ("/assets/site.css", "text/css"),
    ("/assets/site.js", "javascript")
])
def test_site_assets_return_expected_content_types(site_url, path, content_type):
    with urlopen(site_url + path, timeout=5) as response:
        assert response.status == 200
        assert content_type in response.headers.get("Content-Type", "").lower()
        assert response.read(100)


@pytest.mark.http
def test_missing_asset_returns_404(site_url):
    with pytest.raises(HTTPError) as error:
        urlopen(site_url + "/assets/does-not-exist.js", timeout=5)
    assert error.value.code == 404
