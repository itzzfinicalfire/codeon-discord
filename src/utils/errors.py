from typing import Optional


class PteroAPIError(Exception):
    def __init__(self, status: int, message: str, *, details: Optional[dict] = None):
        super().__init__(f"API error {status}: {message}")
        self.status = status
        self.details = details or {}


class PermissionDenied(Exception):
    pass


class ConfigError(Exception):
    pass
