import json

import pytest

from src.site import build, render, validate_config

GOOD = {"headline": "Expo", "message": "Hello", "theme_color": "#002868"}


def test_valid_config_passes():
    validate_config(GOOD)


@pytest.mark.parametrize("color", ["blue", "#12345", "0F1B2D", "#GGGGGG"])
def test_bad_color_rejected(color):
    with pytest.raises(ValueError):
        validate_config({**GOOD, "theme_color": color})


def test_empty_headline_rejected():
    with pytest.raises(ValueError):
        validate_config({**GOOD, "headline": "  "})


def test_render_escapes_html():
    page = render({**GOOD, "headline": "<script>"}, {"build": "1", "commit": "abc", "built_at": "now"})
    assert "<script>" not in page


def test_build_writes_page_and_version(tmp_path):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(GOOD))
    out = build(str(tmp_path / "site"), str(cfg))
    assert (out / "index.html").exists()
    assert "build" in json.loads((out / "version.json").read_text())
