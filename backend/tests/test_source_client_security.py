from datetime import timedelta

from app.core.runtime.official_sources import OfficialSource, OfficialSourceRegistry
from app.core.runtime.source_client import OfficialSourceClient


def test_official_source_client_does_not_follow_unregistered_redirects() -> None:
    registry = OfficialSourceRegistry((
        OfficialSource("s1", "publisher", "https://example.com/source", "ceuta", timedelta(hours=1)),
    ))
    client = OfficialSourceClient(registry)
    try:
        assert client._client.follow_redirects is False
    finally:
        client.close()
