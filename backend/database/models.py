from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text
from sqlalchemy.sql import func
from .connection import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    name = Column(String)
    age = Column(Integer)
    skin_type = Column(String)
    concerns = Column(JSON)  # Stored as JSON array
    allergies = Column(JSON)
    climate = Column(String)
    lifestyle = Column(JSON, nullable=True)
    medical_conditions = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProductDB(Base):
    __tablename__ = "products"
    
    product_id = Column(String, primary_key=True, index=True)
    barcode = Column(String, unique=True, index=True)
    name = Column(String)
    brand = Column(String)
    category = Column(String)
    ingredients = Column(JSON)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FeedbackDB(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    product_id = Column(String, index=True)
    outcome = Column(String)
    rating = Column(Integer)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class ConversationHistory(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    role = Column(String)  # user/assistant
    message = Column(Text)
    agent_used = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
