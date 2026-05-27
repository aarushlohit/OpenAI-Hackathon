from fastapi import FastAPI

from app.api.protection import router as protection_router
from app.api.routes import router
from app.api.runtime import router as runtime_router
from app.core.container import AppContainer
from app.websocket.server import router as websocket_router


def create_app() -> FastAPI:
    app = FastAPI(title="Hermes-X", version="0.1.0")
    app.state.container = AppContainer()
    app.include_router(router)
    app.include_router(protection_router)
    app.include_router(runtime_router)
    app.include_router(websocket_router)
    return app
