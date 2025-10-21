from api.error_handlers import (configure_exception_handlers,
                                configure_middlewares)
from api.routers.event_types_router import router as event_types_router
from api.routers.events_router import router as events_router
from api.routers.medical_records_router import router as medical_records_router
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    configure_middlewares(app)
    configure_exception_handlers(app)
    app.include_router(event_types_router)
    app.include_router(events_router)
    app.include_router(medical_records_router)
    return app


app = create_app()
