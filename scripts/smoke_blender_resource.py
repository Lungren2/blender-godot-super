"""Read blender://scene through the unified MCP and live Blender bridge."""

from __future__ import annotations

import asyncio
import json

from fastmcp import Client

from super_mcp.server import mcp


async def run() -> None:
    async with Client(mcp) as client:
        result = await client.read_resource("blender://scene")
        if not result:
            raise RuntimeError("blender://scene returned no content")

        text = getattr(result[0], "text", None)
        if not isinstance(text, str):
            raise TypeError("blender://scene did not return text JSON")

        print(json.dumps(json.loads(text), indent=2))


if __name__ == "__main__":
    asyncio.run(run())
