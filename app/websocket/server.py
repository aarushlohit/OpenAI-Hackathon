from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/v1/ws")


@router.websocket("/investigations/{correlation_id}")
async def investigation_socket(websocket: WebSocket, correlation_id: UUID) -> None:
    await websocket.accept()
    manager = websocket.app.state.container.websocket_manager
    try:
        async for payload in manager.subscribe(correlation_id, replay=True):
            await websocket.send_text(payload)
    except WebSocketDisconnect:
        return

