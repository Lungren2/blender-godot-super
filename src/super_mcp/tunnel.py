"""Operator helper for OpenAI Secure MCP Tunnel profiles."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess

DEFAULT_PROFILE = "blender-godot-super"
DEFAULT_SERVER_URL = "http://127.0.0.1:8000/mcp"


def _client() -> str:
    executable = shutil.which("tunnel-client")
    if executable is None:
        raise SystemExit(
            "tunnel-client was not found on PATH. Install the current OpenAI "
            "tunnel-client release, then retry."
        )
    return executable


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="blender-godot-super-tunnel")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create a tunnel-client profile for local HTTP.")
    init.add_argument("--tunnel-id", required=True)
    init.add_argument("--profile", default=DEFAULT_PROFILE)
    init.add_argument("--server-url", default=DEFAULT_SERVER_URL)

    doctor = sub.add_parser("doctor", help="Validate the named tunnel-client profile.")
    doctor.add_argument("--profile", default=DEFAULT_PROFILE)

    run = sub.add_parser("run", help="Run the named tunnel-client profile in the foreground.")
    run.add_argument("--profile", default=DEFAULT_PROFILE)
    return parser


def main() -> None:
    args = _parser().parse_args()
    client = _client()
    if args.command in {"init", "run"} and not os.environ.get("CONTROL_PLANE_API_KEY"):
        raise SystemExit("Set CONTROL_PLANE_API_KEY in the environment before using the tunnel.")

    if args.command == "init":
        subprocess.run(
            [
                client,
                "init",
                "--sample",
                "sample_mcp_remote_no_auth",
                "--profile",
                args.profile,
                "--tunnel-id",
                args.tunnel_id,
                "--mcp-server-url",
                args.server_url,
            ],
            check=True,
        )
        return
    if args.command == "doctor":
        subprocess.run([client, "doctor", "--profile", args.profile, "--explain"], check=True)
        return
    subprocess.run([client, "run", "--profile", args.profile], check=True)


if __name__ == "__main__":
    main()
