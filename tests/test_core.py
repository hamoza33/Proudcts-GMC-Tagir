from app.clients.ai_provider import OpenAICompatibleProvider
from app.clients.youcan import YouCanClient
from app.config import Settings

def test_ai_provider_fallback_uses_configurable_base_url():
    content = OpenAICompatibleProvider(Settings(ai_api_key="", ai_base_url="https://www.duckcoding.ai/", ai_model="claude-opus-4-8"))._fallback({"title":"KSA Test Product","category":"Home & Kitchen"})
    assert content.slug == "ksa-test-product"
    assert content.category == "Home & Kitchen"

def test_youcan_discount_variants_are_consistent():
    assert YouCanClient(Settings()).discount_variants(100) == [{"title":"Buy 2 - 20% off","quantity":2,"price":160.0},{"title":"Buy 3 - 30% off","quantity":3,"price":210.0},{"title":"Buy 5 - 30% off","quantity":5,"price":350.0}]
