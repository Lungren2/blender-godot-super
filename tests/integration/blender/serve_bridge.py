"""Keep the real Blender bridge alive for an external MCP client in CI."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "integrations" / "blender" / "addon"))

from blender_godot_super.bridge import _drain_requests, start_bridge, stop_bridge  # noqa: E402

RUN_SECONDS = 45.0
PUMP_INTERVAL_SECONDS = 0.01


def main() -> None:
    start_bridge()
    deadline = time.monotonic() + RUN_SECONDS
    try:
        while time.monotonic() < deadline:
            _drain_requests()
            time.sleep(PUMP_INTERVAL_SECONDS)
    finally:
        stop_bridge()


if __name__ == "__main__":
    main()
