import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("FOODLOOP_DATA", str(tmp_path))
    monkeypatch.delenv("FOODLOOP_USER", raising=False)
    monkeypatch.delenv("FOODLOOP_PASSWORD", raising=False)
    import importlib
    from foodloop import app as appmod
    importlib.reload(appmod)
    return TestClient(appmod.app)


def _img(color=(40, 160, 60)):
    b = io.BytesIO()
    Image.new("RGB", (80, 80), color).save(b, "PNG")
    return b.getvalue()


def test_pages_load(client):
    for url in ("/", "/batches", "/ledger", "/health"):
        assert client.get(url).status_code == 200


def test_full_flow(client):
    r = client.post("/scan", files={"photo": ("a.png", _img(), "image/png")},
                    data={"category": "produce", "source": "Demo Farm"}, follow_redirects=False)
    assert r.status_code == 303
    url = r.headers["location"]
    bid = url.split("/")[-1]
    assert client.get(url).status_code == 200
    assert client.get(f"/image/{bid}").status_code == 200
    client.post(f"/batch/{bid}/review", data={"reviewer": "Sam", "final_route": "people"})
    client.post(f"/batch/{bid}/confirm/donor", data={"name": "Farm"})
    client.post(f"/batch/{bid}/confirm/recipient", data={"name": "Bank"})
    page = client.get(url).text
    assert "Credit issued" in page
    assert "intact" in client.get("/ledger").text.lower()


def test_bad_upload_rejected(client):
    r = client.post("/scan", files={"photo": ("a.txt", b"not an image", "text/plain")},
                    data={"category": "produce"})
    assert r.status_code == 400


def test_oversize_rejected(client):
    r = client.post("/scan", files={"photo": ("a.png", b"0" * (5 * 1024 * 1024 + 10), "image/png")},
                    data={"category": "produce"})
    assert r.status_code == 413


def test_basic_auth(tmp_path, monkeypatch):
    monkeypatch.setenv("FOODLOOP_DATA", str(tmp_path))
    monkeypatch.setenv("FOODLOOP_USER", "u")
    monkeypatch.setenv("FOODLOOP_PASSWORD", "p")
    import importlib
    from foodloop import app as appmod
    importlib.reload(appmod)
    c = TestClient(appmod.app)
    assert c.get("/").status_code == 401
    assert c.get("/", auth=("u", "p")).status_code == 200
