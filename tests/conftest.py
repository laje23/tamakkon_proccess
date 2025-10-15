import pytest


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("RESERCH_HADITH", "5614024534")
    monkeypatch.setenv("RESERCH_CLIP_ID", "5281561767")
    monkeypatch.setenv("RESERCH_LECTURE_ID", "5006265821")
    monkeypatch.setenv("CHANNEL_BALE", "4488387573")
    monkeypatch.setenv("CHANNEL_EITAA", "10732641")
    monkeypatch.setenv("CHANNEL_EITAA_TEST", "10732641")
    