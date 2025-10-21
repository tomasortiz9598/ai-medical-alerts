from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware


class InvalidRequest(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def configure_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def http_exception_handler(request: Request, exc: Exception):  # type: ignore
        return JSONResponse(
            status_code=500,
            content={"error": "Unexpected error. Please try again later."},
        )

    @app.exception_handler(InvalidRequest)
    async def invalid_request_exception_handler(
        request: Request, exc: InvalidRequest  # type: ignore
    ):
        return JSONResponse(
            status_code=400,
            content={"error": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(  # type: ignore
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=400,
            content={"error": str(exc.errors()[0]["msg"])}
            if exc.errors()
            else {"error": "Invalid request"},
        )
