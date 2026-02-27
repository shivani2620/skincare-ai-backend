from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime
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
    description="AI-powered personalized skincare analysis",
    version="2.0.0",
)

# ---------------- STATIC FILES ----------------
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

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
    return {
        "message": "🌸 Skincare Intelligence API",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# ================= USER =================
@app.post("/api/users/create-from-description")
async def create_user_from_description(data: UserProfileCreate, db: Session = Depends(get_db)):

    desc = data.description.lower()

    # Rule-based skin detection (safe demo fallback)
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

    concerns = ["acne"] if "acne" in desc else []

    user_id = str(uuid.uuid4())

    user = User(
        user_id=user_id,
        name=data.name,
        age=data.age,
        skin_type=skin_type,
        concerns=concerns,
        allergies=[],
        climate="temperate",
        lifestyle={},
        medical_conditions=[],
        work_location=getattr(data, "work_location", None)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id": user_id,
        "profile": {
            "skin_type": skin_type,
            "concerns": concerns,
            "confidence": 0.9,
            "work_location": user.work_location
        },
        "message": "Profile created successfully!"
    }

# ================= CHAT =================
@app.post("/api/chat")
async def chat(message: ChatMessage, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == message.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skin_type = user.skin_type.lower()

    # Dynamic personalized logic
    if skin_type == "oily":
        response_text = "For oily skin, use salicylic acid cleanser, niacinamide serum, oil-free moisturizer, and daily sunscreen."
    elif skin_type == "dry":
        response_text = "For dry skin, use hydrating cleanser, hyaluronic acid serum, ceramide moisturizer, and SPF 30+."
    elif skin_type == "sensitive":
        response_text = "For sensitive skin, use fragrance-free gentle cleanser, soothing aloe or centella serum, and mineral sunscreen."
    elif skin_type == "combination":
        response_text = "For combination skin, use gel cleanser, lightweight moisturizer, and balanced active ingredients."
    else:
        response_text = "Use a gentle balanced skincare routine with cleanser, moisturizer, and sunscreen."

    result = {
        "response": response_text,
        "agent_used": "profile_based_demo_agent",
        "confidence": 0.92
    }

    db.add(ConversationHistory(
        user_id=message.user_id,
        role="user",
        message=message.message
    ))

    db.add(ConversationHistory(
        user_id=message.user_id,
        role="assistant",
        message=response_text,
        agent_used="profile_based_demo_agent"
    ))

    db.commit()

    return result

# ================= PRODUCT SCAN =================
@app.post("/api/products/scan")
async def scan_product(scan: ProductScan, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == scan.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    product_data = {
        "product_id": str(uuid.uuid4()),
        "barcode": scan.barcode,
        "name": "Demo Moisturizer",
        "brand": "DemoLab",
        "ingredients": ["Water", "Niacinamide", "Ceramides"],
    }

    analysis = {
        "overall_score": 85,
        "recommendation": "recommended",
        "summary": "Suitable for most skin types",
        "benefits": ["Hydration", "Barrier repair"],
        "warnings": [],
    }

    return {"product": product_data, "analysis": analysis}

# ================= ROUTINE =================
@app.post("/api/routine/generate")
async def generate_routine(user_id: str, budget: str = "mid-range", db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    routine = {
        "morning": ["Cleanser", "Serum", "Moisturizer", "Sunscreen"],
        "night": ["Cleanser", "Treatment", "Moisturizer"],
        "budget": budget
    }

    return routine

# ================= FEEDBACK =================
@app.post("/api/feedback")
async def submit_feedback(feedback: UserFeedback, db: Session = Depends(get_db)):

    entry = FeedbackDB(
        user_id=feedback.user_id,
        product_id=feedback.product_id,
        outcome=feedback.outcome,
        rating=feedback.rating,
        notes=feedback.notes,
    )

    db.add(entry)
    db.commit()

    return {"message": "Feedback saved successfully"}


# ================= LOCAL RUN =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)