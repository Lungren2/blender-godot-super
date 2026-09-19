"""Read blender://scene through the MCP server and real Blender bridge."""

from __future__ import annotations

import asyncio
import json

from mcp import Client

from super_mcp.server import mcp


async def run() -> None:
    async with Client(mcp, raise_exceptions=True) as client:
        result = await client.read_resource("blender://scene")
        if not result.contents:
            raise RuntimeError("blender://scene returned no content")

        content = result.contents[0]
        text = getattr(content, "text", None)
        if not isinstance(text, str):
            raise TypeError("blender://scene did not return text JSON")

        print(json.dumps(json.loads(text), indent=2))


if __name__ == "__main__":
    asyncio.run(run())
