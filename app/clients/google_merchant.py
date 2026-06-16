from app.config import Settings

class GoogleMerchantClient:
    def __init__(self, settings: Settings):
        self.settings = settings
    async def upsert_product(self, product):
        if self.settings.google_target_country.upper() != "SA":
            raise ValueError("Only KSA/SA Google Merchant submissions are enabled")
        return product.google_offer_id or f"demo-gmc-{product.source_id}"
    async def update_availability(self, product):
        return None
