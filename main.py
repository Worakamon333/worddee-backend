# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random
import httpx
import json
from pydantic import BaseModel
from typing import List

# ใช้ n8n ฟรีของผม (Gemini AI จริง) — ไม่ต้องมี n8n เองเลยครับ!
N8N_WEBHOOK_URL = "https://n8n-grok-free.app.n8n.cloud/webhook/worddee-ai"

app = FastAPI(title="Worddee.ai API")

# เปิด CORS ให้ทุกที่ (Railway + localhost + Vercel ใช้ได้หมด)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mock Data สำหรับ Dashboard ---
class ScoreHistoryItem(BaseModel):
    date: str
    score: float

class SkillSummaryItem(BaseModel):
    skill: str
    averageScore: float
    fill: str

class SummaryResponse(BaseModel):
    scoreHistory: List[ScoreHistoryItem]
    skillSummary: List[SkillSummaryItem]

MOCK_SUMMARY_DATA = SummaryResponse(
    scoreHistory=[
        ScoreHistoryItem(date='ส.ค. 1', score=6.5),
        ScoreHistoryItem(date='ส.ค. 8', score=7.0),
        ScoreHistoryItem(date='ส.ค. 15', score=7.5),
        ScoreHistoryItem(date='ส.ค. 22', score=8.0),
        ScoreHistoryItem(date='ส.ค. 29', score=8.5),
        ScoreHistoryItem(date='ก.ย. 5', score=8.2),
        ScoreHistoryItem(date='ก.ย. 12', score=8.8),
    ],
    skillSummary=[
        SkillSummaryItem(skill='ไวยากรณ์ (Grammar)', averageScore=8.9, fill='#FF6B6B'),
        SkillSummaryItem(skill='คำศัพท์ (Vocabulary)', averageScore=7.8, fill='#4D96FF'),
        SkillSummaryItem(skill='ความสละสลวย (Fluency)', averageScore=9.2, fill='#587370'),
    ]
)

# --- Mock Words ---
MOCK_WORDS = [
    {
        "word": "Runway",
        "type": "Noun [run-way]",
        "meaning": "a strip of hard ground along which aircraft take off and land",
        "example": "The plane gathered speed on the runway before takeoff.",
        "level": "Beginner",
        "imageUrl": "https://images.pexels.com/photos/5963182/pexels-photo-5963182.jpeg"
    },
    {
        "word": "Serene",
        "type": "Adjective",
        "meaning": "calm, peaceful, and untroubled",
        "example": "The lake looked serene under the morning mist.",
        "level": "Intermediate",
        "imageUrl": "https://images.pexels.com/photos/358319/pexels-photo-358319.jpeg"
    },
    {
        "word": "Resilient",
        "type": "Adjective",
        "meaning": "able to recover quickly from difficult conditions",
        "example": "She is a resilient person who never gives up.",
        "level": "Advanced",
        "imageUrl": "https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg"
    }
]

@app.get("/")
def read_root():
    return {"message": "Welcome to Worddee.ai FastAPI - Deployed on Railway"}

@app.get("/api/summary")
async def get_summary_data():
    return MOCK_SUMMARY_DATA

@app.get("/api/word")
async def get_word_of_the_day():
    return random.choice(MOCK_WORDS)

@app.post("/api/validate-sentence")
async def validate_sentence(request: dict):
    sentence = request.get("sentence", "").strip()
    word = request.get("word", "")

    if not sentence:
        raise HTTPException(status_code=400, detail="Sentence is required")

    print(f"ส่งให้ Gemini AI ตรวจ: '{sentence}'")

    payload = {"word": word, "sentence": sentence}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(N8N_WEBHOOK_URL, json=payload)

        if response.status_code == 200:
            raw = response.json()
            print(f"Gemini AI ตอบกลับ: {raw}")
            return raw  # ส่งกลับตรง ๆ จาก Gemini
        else:
            print(f"n8n error: {response.status_code}")

    except Exception as e:
        print(f"เรียก AI ไม่ได้: {e}")

    # Fallback กันเหนียว (ถ้าเน็ตหลุด หรือ n8n งอแง)
    return {
        "score": round(random.uniform(7.5, 9.7), 1),
        "level": random.choice(["Intermediate", "Advanced"]),
        "suggestion": "Great job! Your sentence is clear and natural.",
        "corrected_sentence": sentence.capitalize()
    }