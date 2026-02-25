from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

# ✅ FIXED IMPORT PATHS FOR RAILWAY
from backend.models.schemas import *
from backend.database.connection import get_db, engine, Base
from backend.database.models import User, ProductDB, FeedbackDB, ConversationHistory
from backend.agents.orchestrator import OrchestratorAgent
from backend.agents.profile_agent import ProfileIntelligenceAgent
from backend.agents.analysis_agent import AnalysisAgent
from backend.agents.recommendation_agent import RecommendationAgent

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="🤖 Agentic Skincare Intelligence API",
    description="AI-powered personalized skincare analysis",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Agents
orchestrator = OrchestratorAgent()
profile_agent = ProfileIntelligenceAgent()
analysis_agent = AnalysisAgent()
recommendation_agent = RecommendationAgent()


# ================= ROOT =================

@app.get("/")
def root():
    return {
        "message": "🌸 Skincare Intelligence API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ================= USER =================

@app.post("/api/users/create-from-description")
async def create_user_from_description(
    data: UserProfileCreate,
    db: Session = Depends(get_db)
):
    try:

        analysis = await profile_agent.analyze_description(
            data.description
        )

        user_id = str(uuid.uuid4())

        user = User(
            user_id=user_id,
            name=data.name,
            age=data.age,
            skin_type=analysis.get("skin_type", "normal"),
            concerns=analysis.get("concerns", []),
            allergies=analysis.get("allergies", []),
            climate="temperate",
            lifestyle={},
            medical_conditions=[]
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "user_id": user_id,
            "profile": analysis,
            "message": "Profile created successfully!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# ================= CHAT =================

@app.post("/api/chat")
async def chat(
    message: ChatMessage,
    db: Session = Depends(get_db)
):

    try:

        user = db.query(User).filter(
            User.user_id == message.user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        user_profile = {
            "user_id": user.user_id,
            "skin_type": user.skin_type,
            "concerns": user.concerns,
            "allergies": user.allergies
        }

        history = db.query(
            ConversationHistory
        ).filter(
            ConversationHistory.user_id == message.user_id
        ).order_by(
            ConversationHistory.timestamp.desc()
        ).limit(10).all()

        conversation_context = [
            {
                "role": h.role,
                "content": h.message
            }
            for h in reversed(history)
        ]

        result = await orchestrator.route_request(
            message.message,
            user_profile,
            conversation_context
        )

        db.add(
            ConversationHistory(
                user_id=message.user_id,
                role="user",
                message=message.message
            )
        )

        db.add(
            ConversationHistory(
                user_id=message.user_id,
                role="assistant",
                message=result["response"],
                agent_used=result["agent_used"]
            )
        )

        db.commit()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================= PRODUCT SCAN =================

@app.post("/api/products/scan")
async def scan_product(
    scan: ProductScan,
    db: Session = Depends(get_db)
):

    try:

        user = db.query(User).filter(
            User.user_id == scan.user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        product_data = {
            "product_id": str(uuid.uuid4()),
            "barcode": scan.barcode,
            "name": "Demo Moisturizer",
            "brand": "DemoLab",
            "ingredients": [
                "Water",
                "Niacinamide",
                "Ceramides"
            ]
        }

        user_profile = {
            "skin_type": user.skin_type,
            "concerns": user.concerns,
            "allergies": user.allergies,
            "age": user.age
        }

        analysis = await analysis_agent.analyze_product(
            product_data,
            user_profile
        )

        return {
            "product": product_data,
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================= ROUTINE =================

@app.post("/api/routine/generate")
async def generate_routine(
    user_id: str,
    budget: str = "mid-range",
    db: Session = Depends(get_db)
):

    try:

        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        user_profile = {
            "skin_type": user.skin_type,
            "concerns": user.concerns,
            "allergies": user.allergies,
            "age": user.age
        }

        routine = await recommendation_agent.build_routine(
            user_profile,
            budget
        )

        return routine

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================= FEEDBACK =================

@app.post("/api/feedback")
async def submit_feedback(
    feedback: UserFeedback,
    db: Session = Depends(get_db)
):

    try:

        entry = FeedbackDB(
            user_id=feedback.user_id,
            product_id=feedback.product_id,
            outcome=feedback.outcome,
            rating=feedback.rating,
            notes=feedback.notes
        )

        db.add(entry)
        db.commit()

        return {
            "message": "Feedback saved successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================= LOCAL RUN =================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )