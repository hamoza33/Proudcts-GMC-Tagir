import json
from dataclasses import dataclass
import httpx
from slugify import slugify
from app.config import Settings
from app.schemas import PREDEFINED_CATEGORIES

@dataclass
class SeoContent:
    title: str
    description: str
    keywords: list[str]
    slug: str
    category: str
    google_title: str
    google_description: str

class OpenAICompatibleProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
    async def optimize_product(self, product: dict, model: str | None = None) -> SeoContent:
        if not self.settings.ai_api_key:
            return self._fallback(product)
        payload = {
            "model": model or self.settings.ai_model,
            "messages": [
                {"role": "system", "content": "Rewrite ecommerce content for KSA. Return strict JSON with title, description, keywords array, slug, category, google_title, google_description. Follow Google Merchant policies. Category must be one of: " + ", ".join(PREDEFINED_CATEGORIES)},
                {"role": "user", "content": json.dumps(product, ensure_ascii=False)},
            ],
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self.settings.ai_base_url.rstrip("/") + "/v1/chat/completions", headers={"Authorization": f"Bearer {self.settings.ai_api_key}"}, json=payload)
            response.raise_for_status()
        return self._normalize(json.loads(response.json()["choices"][0]["message"]["content"]), product)
    def _fallback(self, product: dict) -> SeoContent:
        title = str(product.get("title") or product.get("name") or "Imported Product").strip()
        category = product.get("category") if product.get("category") in PREDEFINED_CATEGORIES else "General"
        description = product.get("description") or f"{title} متوفر الآن في السعودية بجودة موثوقة وسعر مناسب."
        return SeoContent(title[:150], description, ["KSA", "Saudi Arabia", title[:40]], slugify(title), category, title[:150], description[:5000])
    def _normalize(self, data: dict, product: dict) -> SeoContent:
        fallback = self._fallback(product)
        title = str(data.get("title") or fallback.title).strip()[:150]
        description = str(data.get("description") or fallback.description).strip()
        keywords = data.get("keywords") if isinstance(data.get("keywords"), list) else fallback.keywords
        category = data.get("category") if data.get("category") in PREDEFINED_CATEGORIES else fallback.category
        return SeoContent(title, description, [str(k) for k in keywords][:12], slugify(data.get("slug") or title), category, str(data.get("google_title") or title)[:150], str(data.get("google_description") or description)[:5000])
