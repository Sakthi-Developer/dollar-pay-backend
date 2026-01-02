from typing import List, Dict, Any
import asyncio
from fastapi import WebSocket

class NotificationService:
    _user_connections: Dict[int, List[WebSocket]] = {}
    _admin_connections: List[WebSocket] = []

    @classmethod
    async def connect(cls, websocket: WebSocket, user_id: int, role: str = "user"):
        await websocket.accept()
        if role in ["admin", "super_admin"]:
            cls._admin_connections.append(websocket)
        else:
            if user_id not in cls._user_connections:
                cls._user_connections[user_id] = []
            cls._user_connections[user_id].append(websocket)

    @classmethod
    def disconnect(cls, websocket: WebSocket, user_id: int, role: str = "user"):
        if role in ["admin", "super_admin"]:
            if websocket in cls._admin_connections:
                cls._admin_connections.remove(websocket)
        else:
            if user_id in cls._user_connections and websocket in cls._user_connections[user_id]:
                cls._user_connections[user_id].remove(websocket)
                if not cls._user_connections[user_id]:
                    del cls._user_connections[user_id]

    @classmethod
    async def broadcast_to_admins(cls, message: Dict[str, Any]):
        """Broadcast notification to all connected admins."""
        # Create a copy to avoid modification during iteration issues if we were to remove
        for connection in list(cls._admin_connections):
            try:
                await connection.send_json(message)
            except:
                # If connection is dead, remove it
                if connection in cls._admin_connections:
                    cls._admin_connections.remove(connection)

    @classmethod
    def broadcast_to_admins_sync(cls, message: Dict[str, Any]):
        """Broadcast notification to admins synchronously."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(cls.broadcast_to_admins(message))
        except RuntimeError:
            # No running event loop, notifications will be skipped
            pass

    @classmethod
    async def broadcast_to_user(cls, user_id: int, message: Dict[str, Any]):
        """Broadcast notification to a specific user."""
        if user_id in cls._user_connections:
            for connection in list(cls._user_connections[user_id]):
                try:
                    await connection.send_json(message)
                except:
                    if connection in cls._user_connections[user_id]:
                        cls._user_connections[user_id].remove(connection)

    @classmethod
    def broadcast_to_user_sync(cls, user_id: int, message: Dict[str, Any]):
        """Broadcast notification to user synchronously."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(cls.broadcast_to_user(user_id, message))
        except RuntimeError:
            # No running event loop, notifications will be skipped
            pass

notification_service = NotificationService()
