from sqlalchemy import select
from app.clients.ai_provider import OpenAICompatibleProvider
from app.clients.google_merchant import GoogleMerchantClient
from app.clients.taager import TaagerClient
from app.clients.youcan import YouCanClient
from app.config import get_settings
from app.models import Product
from app.services.images import optimize_image

class ImportService:
    def __init__(self, db):
        self.db = db
        self.settings = get_settings()
        self.taager = TaagerClient(self.settings)
        self.ai = OpenAICompatibleProvider(self.settings)
        self.youcan = YouCanClient(self.settings)
        self.google = GoogleMerchantClient(self.settings)
    async def import_products(self, limit=25, country="SA", model=None):
        if country.upper() not in {"SA", "KSA"}:
            raise ValueError("This system is configured for KSA products only")
        imported = skipped = failed = 0
        errors = []
        for item in await self.taager.list_products(country="SA", limit=limit):
            source_id = str(item.get("id") or item.get("_id") or item.get("sku"))
            if self.db.scalar(select(Product).where(Product.source == "taager", Product.source_id == source_id)):
                skipped += 1
                continue
            try:
                seo = await self.ai.optimize_product(item, model=model)
                qty = int(item.get("stock") or item.get("quantity") or 0)
                product = Product(source_id=source_id, sku=str(item.get("sku") or source_id), country="SA", original_title=str(item.get("title") or ""), seo_title=seo.title, slug=seo.slug, description=seo.description, keywords=", ".join(seo.keywords), category=seo.category, base_price=float(item.get("price") or 0), sale_price=float(item.get("sale_price") or item.get("price") or 0), stock=qty, in_stock=qty > 0, visible=True, image_url=str(item.get("image_url") or ""), sync_status="importing")
                product.image_url = await optimize_image(product.image_url, product.slug)
                product.youcan_product_id = await self.youcan.upsert_product(product)
                product.google_offer_id = await self.google.upsert_product(product)
                product.google_status = "submitted"
                product.sync_status = "synced"
                self.db.add(product)
                self.db.commit()
                imported += 1
            except Exception as exc:
                self.db.rollback()
                failed += 1
                errors.append(f"{source_id}: {exc}")
        return {"imported": imported, "skipped_duplicates": skipped, "failed": failed, "errors": errors}
    async def sync_stock_and_new_products(self):
        changes = 0
        for product in self.db.scalars(select(Product).where(Product.source == "taager")).all():
            stock = await self.taager.get_stock(product.source_id)
            new_stock = int(stock.get("stock") or 0)
            new_in_stock = bool(stock.get("in_stock", new_stock > 0))
            if product.stock != new_stock or product.in_stock != new_in_stock:
                product.stock = new_stock
                product.in_stock = new_in_stock
                if not new_in_stock:
                    product.visible = False
                await self.youcan.update_stock_visibility(product)
                await self.google.update_availability(product)
                product.sync_status = "stock_synced"
                changes += 1
        self.db.commit()
        return {"stock_changes": changes, "new_import": await self.import_products(limit=50, country="SA")}
