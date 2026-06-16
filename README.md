# Taager → YouCan → Google Merchant Center Sync

KSA-only FastAPI dashboard to import Taager/Tejarer products into YouCan, prevent duplicates, rewrite SEO/GMC-safe content through a configurable OpenAI-compatible provider, add buy 2/3/5 discount variants, sync stock, and submit to Google Merchant Center.

The AI provider is configurable and does **not** hard-code the official OpenAI endpoint. Development defaults: DuckCoding, `https://www.duckcoding.ai/`, model `claude-opus-4-8`.

Required production keys: `AI_API_KEY`, `TAAGER_API_KEY`, `YOUCAN_API_KEY`, `YOUCAN_STORE_URL`, `GOOGLE_MERCHANT_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`.
