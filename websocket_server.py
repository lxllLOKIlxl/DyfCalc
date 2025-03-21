import asyncio
import websockets

connected_clients = set()

async def chat_handler(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(chat_handler, "localhost", 8765):
        print("WebSocket-сервер запущено на ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())
