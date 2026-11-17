"""Builds the COMP 491 info page. The output is environment-agnostic:
the SAME build is deployed to staging and later promoted to production."""
import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def load_config(path: str = "site_config.json") -> dict:
    cfg = json.loads(Path(path).read_text())
    validate_config(cfg)
    return cfg


def validate_config(cfg: dict) -> None:
    for key in ("headline", "message", "theme_color"):
        if not str(cfg.get(key, "")).strip():
            raise ValueError(f"site_config.json: '{key}' must not be empty")
    if not HEX_COLOR.match(cfg["theme_color"]):
        raise ValueError(f"theme_color must look like #1A2B3C, got {cfg['theme_color']!r}")
    if len(cfg["headline"]) > 60:
        raise ValueError("headline must be 60 characters or fewer")


def build_info() -> dict:
    return {
        "build": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "commit": os.environ.get("GITHUB_SHA", "local")[:7],
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


def render(cfg: dict, info: dict) -> str:
    e = html.escape
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>COMP 491</title>
<style>
 body {{ margin: 0; font-family: system-ui, sans-serif; background: {cfg['theme_color']}; color: #fff;
        min-height: 100vh; display: flex; flex-direction: column; justify-content: center; padding: 2rem; box-sizing: border-box; }}
 h1 {{ font-size: 2rem; margin: 0 0 .5rem; }}
 p {{ font-size: 1.1rem; opacity: .9; }}
 .build {{ margin-top: 2rem; font-family: monospace; font-size: .95rem; background: rgba(0,0,0,.35);
          display: inline-block; padding: .4rem .7rem; border-radius: 6px; }}
</style></head><body>
<h1>{e(cfg['headline'])}</h1>
<p>{e(cfg['message'])}</p>
<div><span class="build">build #{e(info['build'])} &middot; commit {e(info['commit'])} &middot; {e(info['built_at'])}</span></div>
</body></html>"""


def build(out_dir: str = "site", config_path: str = "site_config.json") -> Path:
    cfg = load_config(config_path)
    info = build_info()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(render(cfg, info))
    (out / "version.json").write_text(json.dumps(info))
    return out


if __name__ == "__main__":
    print(f"Built {build()}/ ")
