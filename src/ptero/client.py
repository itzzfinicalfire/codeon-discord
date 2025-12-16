from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from src import config
from src.utils.errors import PteroAPIError
from src.utils.logger import get_logger

logger = get_logger(__name__)

SAFE_METHODS = {"GET"}


class PteroMeta(BaseModel):
    total: Optional[int]
    count: Optional[int]
    current_page: Optional[int]
    total_pages: Optional[int]


class PteroListResponse(BaseModel):
    data: List[dict]
    meta: Optional[dict]


class PterodactylClient:
    def __init__(self, base_url: str, api_key: str, *, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self, method: str, path: str, *, params: Optional[dict] = None, json: Optional[dict] = None
    ) -> dict:
        url = f"{self.base_url}{path}"
        retries = 3 if method.upper() in SAFE_METHODS else 0
        attempt = 0
        while True:
            attempt += 1
            try:
                response = await self._client.request(
                    method, url, headers=self.headers(), params=params, json=json
                )
            except httpx.RequestError as exc:
                if attempt <= retries:
                    await asyncio.sleep(1.5 * attempt)
                    continue
                raise PteroAPIError(0, f"Network error: {exc}")

            if response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", "1"))
                await asyncio.sleep(retry_after)
                if attempt <= retries:
                    continue

            if response.status_code >= 400:
                try:
                    payload = response.json()
                    errors = payload.get("errors") or []
                    message = "; ".join(err.get("detail", "") for err in errors) or response.text
                except Exception:
                    message = response.text
                raise PteroAPIError(response.status_code, message)

            try:
                return response.json()
            except ValueError:
                return {}

    async def get_paginated(self, path: str, *, page: int = 1, per_page: int = 50) -> PteroListResponse:
        params = {"page": page, "per_page": per_page}
        data = await self._request("GET", path, params=params)
        return PteroListResponse(data=data.get("data", []), meta=data.get("meta"))

    async def get(self, path: str, *, params: Optional[dict] = None) -> dict:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, *, json: Optional[dict] = None) -> dict:
        return await self._request("POST", path, json=json)

    async def patch(self, path: str, *, json: Optional[dict] = None) -> dict:
        return await self._request("PATCH", path, json=json)

    async def delete(self, path: str) -> dict:
        return await self._request("DELETE", path)


class PteroFactory:
    def __init__(self):
        base_url = config.PTERO_BASE_URL
        api_key = config.PTERO_APPLICATION_API_KEY
        if not base_url or not api_key:
            raise RuntimeError(
                "Missing PTERO_BASE_URL or PTERO_APPLICATION_API_KEY in config.py or environment"
            )
        self.client = PterodactylClient(base_url=base_url, api_key=api_key)

    def get_client(self) -> PterodactylClient:
        return self.client
