from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import uuid

# Load environment variables
load_dotenv()

# ---------------- DATABASE ----------------
from database.connection import get_db, engine, Base
from database.models import User, FeedbackDB, ConversationHistory

Base.metadata.create_all(bind=engine)

# ---------------- SCHEMAS ----------------
from models.schemas import UserProfileCreate, ChatMessage, ProductScan, UserFeedback

# ---------------- FASTAPI INIT ----------------
app = FastAPI(
    title="🤖 Agentic Skincare Intelligence API",
    description="Dataset-powered personalized skincare analysis",
    version="3.0.0",
)

# ---------------- LOAD DATASET ----------------
try:
    products_df = pd.read_csv("skincare_products.csv")
    print("✅ Skincare dataset loaded successfully")
except Exception as e:
    print("❌ Failed to load dataset:", e)
    products_df = None

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ROOT =================
@app.get("/")
def root():
    return {"message": "🌸 Skincare Intelligence API", "status": "running", "version": "3.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# ================= CREATE USER =================
@app.post("/api/users/create-from-description")
async def create_user(data: UserProfileCreate, db: Session = Depends(get_db)):

    desc = data.description.lower()

    if "oily" in desc:
        skin_type = "oily"
    elif "dry" in desc:
        skin_type = "dry"
    elif "sensitive" in desc:
        skin_type = "sensitive"
    elif "combination" in desc:
        skin_type = "combination"
    else:
        skin_type = "normal"

    user_id = str(uuid.uuid4())

    user = User(
        user_id=user_id,
        name=data.name,
        age=data.age,
        skin_type=skin_type,
        concerns=[],
        allergies=[],
        climate="temperate",
        lifestyle={},
        medical_conditions=[],
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id": user_id,
        "profile": {"skin_type": skin_type},
        "message": "Profile created successfully!"
    }

# ================= CHAT RECOMMENDATION =================
@app.post("/api/chat")
async def chat(message: ChatMessage, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == message.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if products_df is None:
        raise HTTPException(status_code=500, detail="Dataset not loaded")

    skin_type = user.skin_type.lower()

    recommended = products_df[
        (products_df["skin_type"].str.lower() == skin_type) |
        (products_df["skin_type"].str.lower() == "all")
    ].head(3)

    if recommended.empty:
        response_text = "No suitable products found."
    else:
        product_list = recommended["product_name"].tolist()
        response_text = f"For {skin_type} skin, I recommend: " + ", ".join(product_list)

    return {
        "response": response_text,
        "agent_used": "dataset_recommendation_engine",
        "confidence": 0.95
    }

# ================= BARCODE SCAN =================
@app.post("/api/products/scan")
async def scan_product(scan: ProductScan):

    if products_df is None:
        raise HTTPException(status_code=500, detail="Dataset not loaded")

    product = products_df[products_df["barcode"] == str(scan.barcode)]

    if product.empty:
        raise HTTPException(status_code=404, detail="Product not found")

    product_data = product.iloc[0].to_dict()

    return {
        "product": product_data,
        "analysis": {
            "summary": f"This product contains {product_data['key_ingredients']}.",
            "recommended_for": product_data["skin_type"]
        }
    }

# ================= ROUTINE GENERATION =================
@app.post("/api/routine/generate")
async def generate_routine(user_id: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skin_type = user.skin_type.lower()

    routine_products = products_df[
        (products_df["skin_type"].str.lower() == skin_type) |
        (products_df["skin_type"].str.lower() == "all")
    ]

    morning = routine_products[routine_products["category"] == "Cleanser"]["product_name"].head(1).tolist() + \
              routine_products[routine_products["category"] == "Serum"]["product_name"].head(1).tolist() + \
              routine_products[routine_products["category"] == "Moisturizer"]["product_name"].head(1).tolist() + \
              routine_products[routine_products["category"] == "Sunscreen"]["product_name"].head(1).tolist()

    night = routine_products[routine_products["category"] == "Cleanser"]["product_name"].head(1).tolist() + \
            routine_products[routine_products["category"] == "Treatment"]["product_name"].head(1).tolist() + \
            routine_products[routine_products["category"] == "Moisturizer"]["product_name"].head(1).tolist()

    return {
        "skin_type": skin_type,
        "morning_routine": morning,
        "night_routine": night
    }