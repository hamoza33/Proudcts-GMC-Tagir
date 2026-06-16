from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_product_source"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(40), default="taager")
    source_id: Mapped[str] = mapped_column(String(120), index=True)
    sku: Mapped[str] = mapped_column(String(120), default="")
    country: Mapped[str] = mapped_column(String(8), default="SA")
    original_title: Mapped[str] = mapped_column(String(500))
    seo_title: Mapped[str] = mapped_column(String(500))
    slug: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    keywords: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(120), default="General")
    base_price: Mapped[float] = mapped_column(Float, default=0)
    sale_price: Mapped[float] = mapped_column(Float, default=0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    visible: Mapped[bool] = mapped_column(Boolean, default=True)
    image_url: Mapped[str] = mapped_column(Text, default="")
    youcan_product_id: Mapped[str] = mapped_column(String(120), default="")
    google_offer_id: Mapped[str] = mapped_column(String(120), default="")
    google_status: Mapped[str] = mapped_column(String(80), default="pending")
    sync_status: Mapped[str] = mapped_column(String(80), default="new")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
