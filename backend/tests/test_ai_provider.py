import json

import httpx
import pytest

from app.ai_provider import AnalysisProviderError, GoogleAIStudioProvider, MealImage


def test_google_provider_sends_image_and_parses_structured_response() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": json.dumps({
                                "items": [{
                                    "food_name": "Banana",
                                    "quantity": 1,
                                    "unit": "unidade",
                                    "calories": 90,
                                    "protein": 1,
                                    "carbohydrates": 23,
                                    "fat": 0,
                                    "confidence": 0.91,
                                }]
                            })
                        }]
                    }
                }]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = GoogleAIStudioProvider(
        api_key="test-key",
        model="gemini-test",
        api_url="https://example.test/v1beta/models",
        client=client,
    )
    items = provider.analyze_meal(MealImage(data=b"image", mime_type="image/jpeg"))

    assert items[0].food_name == "Banana"
    request = requests[0]
    assert request.headers["x-goog-api-key"] == "test-key"
    body = json.loads(request.content)
    assert body["generationConfig"]["responseMimeType"] == "application/json"
    assert body["contents"][0]["parts"][0]["inline_data"]["mime_type"] == "image/jpeg"


def test_google_provider_rejects_missing_key() -> None:
    provider = GoogleAIStudioProvider(api_key="", model="gemini-test", client=httpx.Client())
    with pytest.raises(AnalysisProviderError, match="not configured"):
        provider.analyze_meal(MealImage(data=b"image", mime_type="image/jpeg"))


def test_google_provider_rejects_invalid_response() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={"candidates": [{"content": {"parts": [{"text": "not-json"}]}}]},
            )
        )
    )
    provider = GoogleAIStudioProvider(api_key="test-key", client=client)
    with pytest.raises(AnalysisProviderError, match="invalid analysis"):
        provider.analyze_meal(MealImage(data=b"image", mime_type="image/jpeg"))
