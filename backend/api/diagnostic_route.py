"""Operation references for failures before route dependencies finish loading."""
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.responses import JSONResponse

from backend.shared.operation_diagnostics import (
    operation, stage, context_payload, attach_failure, diagnostic_message,
)


class DiagnosticRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def diagnosed(request):
            try:
                with operation(self.name, project_id=request.path_params.get("project_id")):
                    with stage("request_dependencies"):
                        try:
                            return await handler(request)
                        except (HTTPException, RequestValidationError) as exc:
                            # Validation exceptions may embed entire form submissions.
                            attach_failure(exc, {**context_payload(), "exceptions": [{
                                "type": type(exc).__name__, "status_code": getattr(exc, "status_code", 422),
                            }]})
                            raise
            except (HTTPException, RequestValidationError):
                raise
            except Exception as exc:
                return JSONResponse(status_code=500, content={"detail": diagnostic_message(
                    exc, "Operation failed. Export the diagnostic package from Settings."
                )})

        return diagnosed
