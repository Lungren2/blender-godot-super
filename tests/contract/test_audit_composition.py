from __future__ import annotations

import json
from pathlib import Path

from fastmcp import Client, FastMCP

from super_mcp.server import compose_servers


async def test_parent_audit_records_mounted_tool_call(tmp_path: Path) -> None:
    blender = FastMCP("blender-test")
    godot = FastMCP("godot-test")

    @blender.tool
    def blender_echo(text: str) -> dict[str, str]:
        return {"echo": text}

    server = compose_servers(blender, godot, audit_dir=tmp_path)

    async with Client(server) as client:
        result = await client.call_tool("blender_echo", {"text": "hello"})

    assert result.is_error is False
    records = [json.loads(line) for line in (tmp_path / "actions.jsonl").read_text().splitlines()]
    tool_records = [record for record in records if record["kind"] == "tool"]
    assert len(tool_records) == 1
    assert tool_records[0]["name"] == "blender_echo"
    assert tool_records[0]["request"] == {"text": "hello"}
    assert tool_records[0]["status"] == "completed"
