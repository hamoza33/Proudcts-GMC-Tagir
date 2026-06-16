import httpx
from app.config import Settings
from app.schemas import DISCOUNT_VARIANTS

class YouCanClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._access_token = settings.youcan_api_key

    async def _token(self):
        if self._access_token:
            return self._access_token
        if not (self.settings.youcan_client_id and self.settings.youcan_client_secret):
            return ""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(self.settings.youcan_api_base_url.rstrip("/") + "/oauth/token", json={"grant_type": "client_credentials", "client_id": self.settings.youcan_client_id, "client_secret": self.settings.youcan_client_secret})
            response.raise_for_status()
            self._access_token = response.json().get("access_token", "")
        return self._access_token

    async def upsert_product(self, product):
        token = await self._token()
        payload = {"name": product.seo_title, "slug": product.slug, "description": product.description, "price": product.sale_price or product.base_price, "sku": product.sku, "visible": product.visible, "quantity": product.stock, "categories": [product.category], "images": [product.image_url] if product.image_url else [], "variants": self.discount_variants(product.sale_price or product.base_price)}
        if not token:
            return product.youcan_product_id or f"demo-youcan-{product.source_id}"
        url = self.settings.youcan_api_base_url.rstrip("/") + "/products"
        method = "put" if product.youcan_product_id else "post"
        if product.youcan_product_id:
            url += f"/{product.youcan_product_id}"
        async with httpx.AsyncClient(timeout=45) as client:
            response = await getattr(client, method)(url, headers={"Authorization": f"Bearer {token}"}, json=payload)
            response.raise_for_status()
            data = response.json()
        return str(data.get("id") or data.get("product", {}).get("id") or product.youcan_product_id)

    async def update_stock_visibility(self, product):
        token = await self._token()
        if not token or not product.youcan_product_id:
            return None
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.patch(self.settings.youcan_api_base_url.rstrip("/") + f"/products/{product.youcan_product_id}", headers={"Authorization": f"Bearer {token}"}, json={"quantity": product.stock, "visible": product.visible})
            response.raise_for_status()

    def discount_variants(self, base_price):
        variants = []
        for variant in DISCOUNT_VARIANTS:
            quantity = variant["quantity"]
            discount = variant["discount_percent"]
            variants.append({"title": f"Buy {quantity} - {discount}% off", "quantity": quantity, "price": round(base_price * quantity * (1 - discount / 100), 2)})
        return variants
