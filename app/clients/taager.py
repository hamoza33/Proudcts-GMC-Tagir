import httpx
from app.config import Settings

class TaagerClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _headers(self):
        headers = {"Accept": "application/json", "User-Agent": "taager-youcan-gmc-sync/0.1"}
        if self.settings.taager_session_token:
            headers["Cookie"] = f"session={self.settings.taager_session_token}"
            headers["Authorization"] = f"Bearer {self.settings.taager_session_token}"
        if self.settings.taager_api_key:
            headers["Authorization"] = f"Bearer {self.settings.taager_api_key}"
        return headers

    async def list_products(self, country="SA", limit=50):
        if not (self.settings.taager_session_token or self.settings.taager_api_key):
            return self._demo_products(country, limit)
        params = {"country": country, "limit": limit}
        if self.settings.taager_category_id:
            params["category"] = self.settings.taager_category_id
        async with httpx.AsyncClient(timeout=45, follow_redirects=True) as client:
            response = await client.get(self.settings.taager_api_base_url.rstrip("/") + self.settings.taager_products_path, headers=self._headers(), params=params)
            response.raise_for_status()
            try:
                data = response.json()
            except ValueError:
                return []
        products = data.get("products") or data.get("data") or data.get("items") or data
        return products[:limit] if isinstance(products, list) else []

    async def get_stock(self, source_id):
        if not (self.settings.taager_session_token or self.settings.taager_api_key):
            return {"source_id": source_id, "stock": 12, "in_stock": True}
        path = self.settings.taager_stock_path.format(source_id=source_id)
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(self.settings.taager_api_base_url.rstrip("/") + path, headers=self._headers())
            response.raise_for_status()
            data = response.json()
        stock = data.get("stock") or data.get("quantity") or data.get("availableQuantity") or 0
        return {"source_id": source_id, "stock": int(stock), "in_stock": bool(data.get("in_stock", int(stock) > 0))}

    def _demo_products(self, country, limit):
        return [
            {"id": "demo-ksa-001", "sku": "KSA-DEMO-001", "title": "Premium Arabic Coffee Maker", "description": "Easy-to-use coffee maker suitable for Arabic coffee preparation.", "price": 149.0, "sale_price": 129.0, "stock": 18, "country": country, "category": "Home & Kitchen", "image_url": ""},
            {"id": "demo-ksa-002", "sku": "KSA-DEMO-002", "title": "Wireless Mini Hair Styler", "description": "Portable styling tool for quick hair care routines.", "price": 99.0, "sale_price": 79.0, "stock": 0, "country": country, "category": "Beauty & Personal Care", "image_url": ""},
        ][:limit]
