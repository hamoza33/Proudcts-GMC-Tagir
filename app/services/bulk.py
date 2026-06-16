from sqlalchemy import select
from app.models import Product

def apply_bulk_price_change(db, product_ids, mode, amount):
    count = 0
    for p in db.scalars(select(Product).where(Product.id.in_(product_ids))).all():
        p.sale_price = round(p.sale_price * (1 + amount / 100), 2) if mode == "percent" else round(p.sale_price + amount, 2)
        p.sync_status = "needs_push"
        count += 1
    db.commit()
    return count

def apply_bulk_visibility(db, product_ids, visible):
    count = 0
    for p in db.scalars(select(Product).where(Product.id.in_(product_ids))).all():
        p.visible = visible
        p.sync_status = "needs_push"
        count += 1
    db.commit()
    return count
