"""Domain-level and API-level exception hierarchy.

Keeping exceptions in `core` allows both the domain layer and the API layer to
depend on a single, stable contract without the domain depending on FastAPI.
"""


class AppError(Exception):
    """Base class for all application errors."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"


class CalculationEngineError(AppError):
    status_code = 502
    error_code = "calculation_engine_error"


class MarketDataUnavailableError(CalculationEngineError):
    error_code = "market_data_unavailable"
