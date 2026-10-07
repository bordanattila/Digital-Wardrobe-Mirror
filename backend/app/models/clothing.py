from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Clothing(Base):
    __tablename__ = "ClothingItem"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item_color: Mapped[str] = mapped_column(String(20), nullable=False)
    item_size: Mapped[str] = mapped_column(String(10), nullable=False)
    item_category: Mapped[str] = mapped_column(String(20), nullable=False)
    item_subcategory: Mapped[str] = mapped_column(String(50), nullable=False)
    item_image_path: Mapped[str] = mapped_column(String(255), nullable=False)
