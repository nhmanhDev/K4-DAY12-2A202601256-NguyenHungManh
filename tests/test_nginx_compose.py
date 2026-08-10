"""Regression checks for the optional Nginx load-balancer topology."""

from __future__ import annotations

import yaml


def test_nginx_is_the_only_public_gateway(repo_root):
    compose = yaml.safe_load((repo_root / "docker-compose.yml").read_text(encoding="utf-8"))

    chat = compose["services"]["chat"]
    nginx = compose["services"]["nginx"]

    assert chat.get("ports") is None
    assert chat["expose"] == ["8000"]
    assert nginx["image"] == "nginx:1.27-alpine"
    assert nginx["ports"] == ["8000:80"]
    assert "./nginx/nginx.conf:/etc/nginx/nginx.conf:ro" in nginx["volumes"]
    assert "chat" in nginx["depends_on"]
