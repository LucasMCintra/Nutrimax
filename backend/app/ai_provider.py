from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from typing import Any, List, Optional, Protocol

import httpx

from app.core.config import settings
from app.schemas import MealAnalysisItemBase


class AnalysisProviderError(Exception):
    """Erro controlado ao consultar o provedor de análise."""

    def __init__(self, message: str, code: str = "provider_error") -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class MealImage:
    data: bytes
    mime_type: str


class MealAnalysisProvider(Protocol):
    def analyze_meal(self, image: MealImage) -> List[MealAnalysisItemBase]:
        ...


class GoogleAIStudioProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_backoff_seconds: Optional[float] = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else (settings.google_ai_studio_api_key or settings.gemini_api_key)
        self.model = model or settings.gemini_model
        self.api_url = (api_url or settings.gemini_api_url).rstrip("/")
        self.timeout = timeout or settings.gemini_timeout_seconds
        self.max_retries = max_retries if max_retries is not None else settings.gemini_max_retries
        self.retry_backoff_seconds = retry_backoff_seconds if retry_backoff_seconds is not None else settings.gemini_retry_backoff_seconds
        self.client = client

    def analyze_meal(self, image: MealImage) -> List[MealAnalysisItemBase]:
        if not self.api_key:
            raise AnalysisProviderError("Google AI Studio is not configured", code="provider_not_configured")

        payload = {
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": image.mime_type,
                            "data": base64.b64encode(image.data).decode("ascii"),
                        }
                    },
                    {
                        "text": (
                            "Analise a imagem de uma refeição. Identifique somente alimentos visíveis "
                            "e estime quantidade e nutrientes. Responda exclusivamente com JSON válido "
                            "no formato {\"items\":[{\"food_name\":string,\"quantity\":number,"
                            "\"unit\":string,\"calories\":number,\"protein\":number,"
                            "\"carbohydrates\":number,\"fat\":number,\"confidence\":number}]}"
                        ),
                    },
                ],
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "items": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "food_name": {"type": "STRING"},
                                    "quantity": {"type": "NUMBER"},
                                    "unit": {"type": "STRING"},
                                    "calories": {"type": "NUMBER"},
                                    "protein": {"type": "NUMBER"},
                                    "carbohydrates": {"type": "NUMBER"},
                                    "fat": {"type": "NUMBER"},
                                    "confidence": {"type": "NUMBER"},
                                },
                                "required": [
                                    "food_name", "quantity", "unit", "calories",
                                    "protein", "carbohydrates", "fat", "confidence",
                                ],
                            },
                        }
                    },
                    "required": ["items"],
                },
            },
        }
        url = f"{self.api_url}/{self.model}:generateContent"
        headers = {"x-goog-api-key": self.api_key, "Content-Type": "application/json"}

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                if self.client is not None:
                    response = self.client.post(url, headers=headers, json=payload, timeout=self.timeout)
                else:
                    with httpx.Client(timeout=self.timeout) as client:
                        response = client.post(url, headers=headers, json=payload)
                if response.status_code not in {429, 500, 502, 503, 504}:
                    response.raise_for_status()
                    break
                last_error = f"HTTP {response.status_code}"
            except httpx.TimeoutException as error:
                last_error = "timeout"
            except httpx.HTTPError as error:
                raise AnalysisProviderError("Google AI Studio request failed", code="provider_request_failed") from error
            if attempt < self.max_retries:
                time.sleep(self.retry_backoff_seconds * (attempt + 1))
        else:
            code = "provider_timeout" if last_error == "timeout" else "provider_unavailable"
            raise AnalysisProviderError(f"Google AI Studio temporarily unavailable ({last_error})", code=code)

        try:
            body = response.json()
            text = body["candidates"][0]["content"]["parts"][0]["text"]
            parsed: Any = json.loads(text)
            items = parsed["items"]
            return [MealAnalysisItemBase.model_validate(item) for item in items]
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise AnalysisProviderError("Google AI Studio returned an invalid analysis", code="provider_invalid_response") from error
