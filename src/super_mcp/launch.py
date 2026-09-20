"""Command-line launcher for stdio and loopback Streamable HTTP modes."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from super_mcp.astra import ASTRA_GODOT_TOOLSETS

_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="blender-godot-super")
    parser.add_argument("--transport", choices=("stdio", "http"), default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--path", default="/mcp")
    parser.add_argument(
        "--profile",
        choices=("standard", "astra"),
        default="standard",
        help="Astra seeds bounded Godot toolsets and enables audit logging by default.",
    )
    parser.add_argument("--audit-dir", type=Path)
    return parser


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    if args.transport == "http" and args.host not in _LOOPBACK_HOSTS:
        parser.error(
            "HTTP mode is intentionally loopback-only. Use Secure MCP Tunnel or an "
            "authenticated reverse proxy instead of binding this server publicly."
        )

    audit_dir = args.audit_dir
    if args.profile == "astra":
        os.environ.setdefault("GODOT_MCP_DEFAULT_TOOLSETS", ASTRA_GODOT_TOOLSETS)
        audit_dir = audit_dir or Path(".super-mcp") / "audit"

    from super_mcp.server import build_server

    server = build_server(audit_dir=audit_dir)
    if args.transport == "stdio":
        server.run()
        return
    server.run(
        transport="http",
        host=args.host,
        port=args.port,
        path=args.path,
    )


if __name__ == "__main__":
    main()
