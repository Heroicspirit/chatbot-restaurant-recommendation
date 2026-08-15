from sqlalchemy import Column, String, Integer, Float, Boolean, Text
from database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    restaurant_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    area = Column(String)
    address = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    cuisine = Column(String)
    price_level = Column(String)
    avg_price_per_person = Column(Integer)
    rating = Column(Float)
    review_count = Column(Integer)
    veg_available = Column(Boolean)
    serves_both = Column(Boolean, default=False)
    ambience_tags = Column(String)
    suitable_for = Column(String)
    opening_hours = Column(String)
    source_url = Column(String)
    description = Column(String)
    data_confidence = Column(String)
