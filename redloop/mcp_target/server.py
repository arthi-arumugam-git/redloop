"""Stdio MCP server exposing a MirrorTarget with the config's exact tool schemas."""

from __future__ import annotations

import json
from typing import Any

from redloop.mcp_target.core import MirrorTarget


def build_server(target: MirrorTarget):
    # Imported lazily so the core package keeps zero runtime dependencies.
    from mcp import types
    from mcp.server.lowlevel import Server

    server = Server(f"redloop-{target.config['server_name']}")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [types.Tool(name=spec["name"], description=spec.get("description", ""),
                           inputSchema=spec["input_schema"])
                for spec in target.config["tools"]]

    # validate_input=False: a schema-invalid call is still the agent's decision
    # and must reach the log (core.call records errors too).
    @server.call_tool(validate_input=False)
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        result = target.call(name, arguments)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    return server


async def serve_stdio(target: MirrorTarget) -> None:
    from mcp.server.stdio import stdio_server

    server = build_server(target)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
