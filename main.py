import asyncio
import uvicorn
from config import TOKEN
from events import setup_event_handlers
from bot import client
from server import app


async def main():
    setup_event_handlers(client)
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        client.start(TOKEN)
    )

asyncio.run(main())
