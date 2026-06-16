from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "Taager YouCan GMC Sync"
    database_url: str = "sqlite:///./data/app.db"
    public_base_url: str = "https://gmc.shopinzo.bond"
    ai_provider_name: str = "DuckCoding"
    ai_base_url: str = "https://www.duckcoding.ai/"
    ai_model: str = "claude-opus-4-8"
    ai_api_key: str = ""
    taager_api_key: str = ""
    taager_session_token: str = ""
    taager_api_base_url: str = "https://merchant.api.taager.com/api"
    taager_products_path: str = "/variant-groups/search"
    taager_stock_path: str = "/api/products/{source_id}/stock"
    taager_category_id: str = "13"
    youcan_api_key: str = ""
    youcan_api_base_url: str = "https://api.youcan.shop"
    youcan_store_url: str = "https://shpanay.youcan.store/"
    youcan_client_id: str = ""
    youcan_client_secret: str = ""
    google_merchant_id: str = ""
    google_service_account_json: str = ""
    google_target_country: str = "SA"
    google_content_language: str = "ar"
    sync_enabled: bool = False

@lru_cache
def get_settings():
    return Settings()
