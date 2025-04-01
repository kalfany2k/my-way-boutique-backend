from .database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    surname = Column(String, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    role = Column(String, default="regular", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    item_gender = Column(String, nullable=False)
    type = Column(String, nullable=False)
    categories = Column(ARRAY(String), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    rating = Column(Numeric(10, 2), nullable=True) # TO BE CHANGED. ONLY FOR TESTING
    primary_image = Column(String, nullable=True)
    secondary_images = Column(ARRAY(String), nullable=True)
    total_sales = Column(Integer, nullable=False, server_default=text('0'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class ProductSet(Base):
    __tablename__ = "product_sets"

    id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    set_type = Column(String, nullable=False)
    primary_product_ids = Column(ARRAY(String), nullable=False)
    secondary_product_ids = Column(ARRAY(String), nullable=True)

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    guest_id = Column(String, nullable=True)
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"))
    product_name = Column(String, ForeignKey("products.name", ondelete="CASCADE"))
    product_price = Column(Integer, nullable=False)
    product_type = Column(String, nullable=False)
    product_primary_image = Column(String, nullable=False)
    personalised_fields = Column(JSON, nullable=True)
    hash = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, server_default=text('1'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"))
    message = Column(String, nullable=True)
    stars = Column(Integer, nullable=False)
    author_surname = Column(String, nullable=False)
    author_name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))

    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uix_user_product_reviews'),
    )

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, nullable=False)
    shipping_address = Column(JSON, nullable=False)
    payment_intent_id = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"))
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    personalization = Column(JSON, nullable=True)