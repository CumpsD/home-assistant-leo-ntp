"""LeoNTP API Client."""
from __future__ import annotations

from .const import DEFAULT_UPDATE_INTERVAL

class LeoNtpClient:
    """LeoNTP client."""

    def __init__(
        self,
        host: str | None = None,
        update_interval: int | None = None,
    ) -> None:
        """Initialize LeoNTP Client."""
        self.host = host
        self.update_interval = (
            update_interval if update_interval else DEFAULT_UPDATE_INTERVAL
        )
