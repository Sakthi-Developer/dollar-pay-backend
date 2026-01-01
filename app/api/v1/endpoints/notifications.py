from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.orm import Session
from app.services.notification_service import notification_service
from app.core.security import get_current_user_ws

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int, 
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time notifications.
    """
    # Validate token
    auth_result = get_current_user_ws(token)
    if not auth_result:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    token_user_id, role = auth_result
    
    # If it's a regular user, ensure they match the requested user_id
    if role == "user" and token_user_id != user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await notification_service.connect(websocket, token_user_id, role)
    try:
        while True:
            # Keep the connection alive and listen for any client messages (optional)
            data = await websocket.receive_text()
            # You could handle client acks or messages here
    except WebSocketDisconnect:
        notification_service.disconnect(websocket, token_user_id, role)
