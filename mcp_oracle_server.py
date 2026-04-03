import asyncio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types
import yfinance as yf

server = Server("fetchai-oracle")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_live_price",
            description="Fetch strictly current real-time pricing data representing the decentralized ground truth oracle. Connects to standard AgentFi execution loops natively.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "The stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    if name == "get_live_price":
        ticker = arguments.get("ticker", "").upper()
        try:
            stock = yf.Ticker(ticker)
            live_price = stock.info.get('currentPrice', stock.info.get('lastPrice', stock.info.get('regularMarketPrice')))
            if live_price is None:
                hist = stock.history(period="1d")
                if not hist.empty: live_price = hist['Close'].iloc[-1]
            return [types.TextContent(type="text", text=str(live_price) if live_price else "Oracle Lookup Error")]
        except:
            return [types.TextContent(type="text", text="Oracle Execution Failed")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="fetchai-oracle",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
