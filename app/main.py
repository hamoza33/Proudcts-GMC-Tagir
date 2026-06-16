from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from app.config import get_settings
from app.database import Base, engine, get_db
from app.models import Product
from app.schemas import PREDEFINED_CATEGORIES
from app.services.bulk import apply_bulk_price_change, apply_bulk_visibility
from app.services.importer import ImportService
from app.services.scheduler import start_scheduler

Base.metadata.create_all(bind=engine)
app = FastAPI(title=get_settings().app_name)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
async def dashboard(request: Request, db=Depends(get_db)):
    products = db.scalars(select(Product).order_by(Product.updated_at.desc())).all()
    stats = {"total": len(products), "visible": sum(1 for p in products if p.visible), "out_of_stock": sum(1 for p in products if not p.in_stock), "gmc_submitted": sum(1 for p in products if p.google_status == "submitted")}
    return templates.TemplateResponse(request, "dashboard.html", {"products": products, "stats": stats, "categories": PREDEFINED_CATEGORIES, "settings": get_settings()})

@app.post("/import")
async def import_products(limit: int = Form(25), model: str = Form(""), db=Depends(get_db)):
    await ImportService(db).import_products(limit=limit, country="SA", model=model or None)
    return RedirectResponse("/", status_code=303)

@app.post("/sync")
async def sync_now(db=Depends(get_db)):
    await ImportService(db).sync_stock_and_new_products()
    return RedirectResponse("/", status_code=303)

@app.post("/bulk/price")
async def bulk_price(ids: str = Form(""), mode: str = Form("percent"), amount: float = Form(0), db=Depends(get_db)):
    apply_bulk_price_change(db, [int(i) for i in ids.split(",") if i.strip().isdigit()], mode, amount)
    return RedirectResponse("/", status_code=303)

@app.post("/bulk/visibility")
async def bulk_visibility(ids: str = Form(""), visible: str = Form("true"), db=Depends(get_db)):
    apply_bulk_visibility(db, [int(i) for i in ids.split(",") if i.strip().isdigit()], visible == "true")
    return RedirectResponse("/", status_code=303)

@app.get("/settings")
async def settings_page(request: Request):
    return templates.TemplateResponse(request, "settings.html", {"settings": get_settings()})

@app.get("/health")
async def health():
    return {"ok": True, "country": "SA", "ai_provider": get_settings().ai_provider_name}
