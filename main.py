#!/usr/bin/env python3
"""
RSS MCP Server - Fresh version based on working test
"""
import asyncio
import sys
import json
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, Resource

# Your existing modules
from processor import RSSProcessor
from state import StateManager

class RSSMCPServer:
    def __init__(self):
        self.processor = RSSProcessor()
        self.state_manager = StateManager()

    async def initialize(self):
        """Initialize the RSS processor and state manager"""
        await self.processor.initialize()

    async def get_unread_articles(self) -> list:
        """Get unread articles from all configured feeds"""
        await self.processor.update_feeds()
        all_articles = await self.processor.get_all_articles()
        unread = self.state_manager.get_unread_items(all_articles)
        return unread

    async def mark_articles_read(self, article_ids: list = None):
        """Mark articles as read"""
        if article_ids:
            for article_id in article_ids:
                self.state_manager.mark_read(article_id)
        else:
            all_articles = await self.processor.get_all_articles()
            self.state_manager.mark_all_read(all_articles)

# Create the MCP server instance
app = Server("rss-mcp-server")
rss_server = RSSMCPServer()

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available RSS resources"""
    return [
        Resource(
            uri="rss://feeds/unread",
            name="Unread RSS Articles",
            description="Get all unread articles from configured RSS feeds",
            mimeType="application/json",
        ),
        Resource(
            uri="rss://feeds/all",
            name="All RSS Articles",
            description="Get all articles from configured RSS feeds",
            mimeType="application/json",
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read RSS resource content"""
    if uri == "rss://feeds/unread":
        unread_articles = await rss_server.get_unread_articles()
        return json.dumps(unread_articles, indent=2)
    elif uri == "rss://feeds/all":
        all_articles = await rss_server.processor.get_all_articles()
        return json.dumps(all_articles, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="update_rss_feeds",
            description="Fetch latest articles from all configured RSS feeds",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="get_unread_articles",
            description="Get all unread articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of articles to return",
                        "default": 50
                    }
                },
                "required": []
            },
        ),
        Tool(
            name="mark_articles_read",
            description="Mark articles as read",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of article IDs to mark as read. If empty, marks all as read."
                    }
                },
                "required": []
            },
        ),
        Tool(
            name="search_articles",
            description="Search articles by keywords in title or content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query keywords"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by specific tags"
                    }
                },
                "required": ["query"]
            },
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool calls"""
    if arguments is None:
        arguments = {}

    try:
        if name == "update_rss_feeds":
            await rss_server.processor.update_feeds()
            return [TextContent(type="text", text="RSS feeds updated successfully")]

        elif name == "get_unread_articles":
            limit = arguments.get("limit", 50)
            articles = await rss_server.get_unread_articles()

            # Limit results
            if limit and len(articles) > limit:
                articles = articles[:limit]

            result = {
                "count": len(articles),
                "articles": articles
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "mark_articles_read":
            article_ids = arguments.get("article_ids", [])
            await rss_server.mark_articles_read(article_ids)

            if article_ids:
                msg = f"Marked {len(article_ids)} articles as read"
            else:
                msg = "Marked all articles as read"

            return [TextContent(type="text", text=msg)]

        elif name == "search_articles":
            query = arguments.get("query", "")
            tags = arguments.get("tags", [])

            results = await rss_server.processor.search_articles(query, tags)
            return [TextContent(type="text", text=json.dumps(results, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point for MCP server"""
    try:
        # Initialize the RSS server
        await rss_server.initialize()
        print("RSS MCP Server initialized successfully", file=sys.stderr)

        async with stdio_server() as (read_stream, write_stream):
            # Create proper notification options with correct parameter names
            notification_options = NotificationOptions(
                tools_changed=True,  # We can notify about tool changes
                resources_changed=True,  # We have RSS resources
                prompts_changed=False  # We don't have prompts
            )

            # Empty experimental capabilities dict
            experimental_capabilities = {}

            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="rss-mcp-server",
                    server_version="1.0.0",
                    capabilities=app.get_capabilities(notification_options, experimental_capabilities),
                ),
            )

    except Exception as e:
        print(f"Error starting RSS MCP Server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())
