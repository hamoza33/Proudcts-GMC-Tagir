from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import get_settings
scheduler = AsyncIOScheduler()
def start_scheduler():
    if get_settings().sync_enabled and not scheduler.running:
        scheduler.start()
