"""Utility helpers for reusable greeting logic."""

from __future__ import annotations


def hello_world() -> str:
    """Return the canonical greeting for diagnostics and smoke tests."""

    # Keep this deterministic so monitoring can rely on an exact value.
    return "Hello, World!"
