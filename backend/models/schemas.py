from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

# =========================
# ENUMS
# =========================

class SkinType(str, Enum):
    oily = "oily"
    dry = "dry"
    combination = "combination"
    sensitive = "sensitive"
    normal = "normal"

class Climate(str, Enum):
    tropical = "tropical"
    dry = "dry"
    cold = "cold"
    temperate = "temperate"

# =========================
# USER MODELS
# =========================

class UserProfile(BaseModel):
    user_id: str
    email: Optional[EmailStr] = None
    name: str
    age: int = Field(..., ge=10, le=100)
    skin_type: SkinType
    concerns: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    climate: Climate
    lifestyle: Optional[Dict] = None
    medical_conditions: List[str] = Field(default_factory=list)
    work_location: Optional[str] = None  # ✅ New field
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfileCreate(BaseModel):
    name: str
    age: int = Field(..., ge=10, le=100)
    description: str
    work_location: Optional[str] = None  # ✅ Allow frontend to send work location

# =========================
# PRODUCT MODELS
# =========================

class Product(BaseModel):
    product_id: str
    barcode: str
    name: str
    brand: str
    category: Optional[str] = None
    ingredients: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None

class ProductScan(BaseModel):
    user_id: str
    barcode: str

# =========================
# ANALYSIS MODELS
# =========================

class IngredientAnalysis(BaseModel):
    ingredient: str
    benefits: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    suitability_score: float = Field(..., ge=0, le=100)
    evidence_level: str
    explanation: str

class ProductAnalysisResult(BaseModel):
    product: Product
    overall_score: int = Field(..., ge=0, le=100)
    recommendation: str
    ingredient_analyses: List[IngredientAnalysis] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    interactions: List[str] = Field(default_factory=list)
    alternatives: List[Dict] = Field(default_factory=list)
    breakout_risk: float = Field(..., ge=0, le=100)

# =========================
# CHAT MODELS
# =========================

class ChatMessage(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    confidence: float = Field(..., ge=0, le=1)
    follow_up_questions: Optional[List[str]] = None

# =========================
# FEEDBACK MODELS
# =========================

class UserFeedback(BaseModel):
    user_id: str
    product_id: str
    outcome: str  # breakout / improved / no_change
    rating: int = Field(..., ge=1, le=5)
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)