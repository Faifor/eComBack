from __future__ import annotations

from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import request_id_ctx

PROBLEM_JSON = "application/problem+json"


def _build_problem(*, request: Request, status: int, title: str, detail: str, errors: list | None = None) -> dict:
    problem = {
        "type": f"https://httpstatuses.com/{status}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": str(request.url.path),
        "request_id": request_id_ctx.get(),
    }
    if errors:
        problem["errors"] = errors
    return problem


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        status_code = int(exc.status_code)
        title = HTTPStatus(status_code).phrase if status_code in HTTPStatus._value2member_map_ else "HTTP Error"
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return JSONResponse(
            status_code=status_code,
            content=_build_problem(request=request, status=status_code, title=title, detail=detail),
            media_type=PROBLEM_JSON,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_build_problem(
                request=request,
                status=422,
                title="Unprocessable Entity",
                detail="Request validation failed",
                errors=exc.errors(),
            ),
            media_type=PROBLEM_JSON,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, _: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=_build_problem(
                request=request,
                status=500,
                title="Internal Server Error",
                detail="Unexpected server error",
            ),
            media_type=PROBLEM_JSON,
        )