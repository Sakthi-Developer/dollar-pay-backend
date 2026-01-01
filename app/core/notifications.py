from typing import List
import asyncio

websocket_connections: List = []

def broadcast_notification(message: dict):
    """Broadcast notification to all connected WebSocket clients."""
    for connection in websocket_connections:
        try:
            asyncio.create_task(connection.send_json(message))
        except:
            websocket_connections.remove(connection)