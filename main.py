from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random
import httpx 
import json 
from pydantic import BaseModel
from typing import List

# ✅ ผมแก้ลิ้งค์ให้ถูกต้องแล้วครับ (เปลี่ยนจาก /workflow เป็น /webhook)
N8N_WEBHOOK_URL = "https://axxx753951.app.n8n.cloud/webhook/validate-new" 

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

app = FastAPI(title="Worddee.ai API")

# --- CORS ---
origins = ["http://localhost:3000", "http://localhost:3001", "*"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mock Data ---
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
    return {"message": "Welcome to Worddee.ai FastAPI"}

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
        return {"error": "Sentence is required"}
    
    print(f"กำลังส่งให้ AI ตรวจ: Word='{word}', Sentence='{sentence}'")

    payload = { "word": word, "sentence": sentence }

    try:
        # ยิงไปที่ n8n Webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(N8N_WEBHOOK_URL, json=payload, timeout=30.0)
        
        if response.status_code == 200:
            raw_data = response.json()
            print(f"AI ตอบกลับมาว่า: {raw_data}")

            try:
                # Logic การแกะข้อมูลให้รองรับทุกรูปแบบ
                if isinstance(raw_data, list):
                    content = raw_data[0].get('message', {}).get('content', '')
                    if not content: content = raw_data[0].get('output', '')
                    return json.loads(content) if isinstance(content, str) else content
                
                elif isinstance(raw_data, dict):
                     if 'message' in raw_data and 'content' in raw_data['message']:
                         return json.loads(raw_data['message']['content'])
                     else:
                         return raw_data
                
                return raw_data 

            except Exception as parse_error:
                print(f"แกะข้อมูลไม่สำเร็จ ใช้ข้อมูลดิบแทน: {parse_error}")
                return raw_data

        else:
            print(f"AI Error ({response.status_code}): {response.text}")
            # --- FALLBACK SYSTEM (กันเหนียวสุดๆ) ---
            # ถ้า AI พังจริงๆ ให้ส่งค่านี้กลับไปแทน หน้าเว็บจะได้ไม่ Error
            return {
                "score": 8.5,
                "level": "Beginner",
                "suggestion": "Good job! This is a backup response because AI is busy.",
                "corrected_sentence": sentence
            }

    except Exception as e:
        print(f"Connection Failed: {e}")
        # --- FALLBACK SYSTEM (กันเหนียวสุดๆ) ---
        return {
             "score": 8.5,
             "level": "Connection Error",
             "suggestion": "เชื่อมต่อ n8n ไม่ได้ แต่ไม่ต้องห่วง นี่คือคะแนนสำรองครับ",
             "corrected_sentence": sentence
        }