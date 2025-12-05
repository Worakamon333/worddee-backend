from pydantic import BaseModel, Field
from typing import List

# 1. โครงสร้างข้อมูลสำหรับแผนภูมิประวัติคะแนน (Line Chart)
class ScoreHistoryItem(BaseModel):
    date: str = Field(..., description="วันที่ เช่น 'ส.ค. 1'")
    score: float = Field(..., description="คะแนนความถูกต้อง (0.0 - 10.0)")

# 2. โครงสร้างข้อมูลสำหรับแผนภูมิสรุปทักษะ (Radial Bar Chart)
class SkillSummaryItem(BaseModel):
    skill: str = Field(..., description="ชื่อทักษะ เช่น 'ไวยากรณ์'")
    averageScore: float = Field(..., description="คะแนนเฉลี่ยสำหรับทักษะนั้น (0.0 - 10.0)")
    fill: str = Field(..., description="รหัสสีสำหรับแผนภูมิ เช่น '#FF6B6B'")

# 3. โครงสร้างข้อมูลหลักสำหรับ Dashboard Summary Response
class SummaryResponse(BaseModel):
    scoreHistory: List[ScoreHistoryItem]
    skillSummary: List[SkillSummaryItem]
    
    # เพิ่มตัวอย่างข้อมูลสำหรับเอกสาร Swagger
    class Config:
        schema_extra = {
            "example": {
                "scoreHistory": [
                    {"date": "ส.ค. 1", "score": 7.5},
                    {"date": "ส.ค. 8", "score": 8.0},
                ],
                "skillSummary": [
                    {"skill": "ไวยากรณ์ (Grammar)", "averageScore": 8.9, "fill": "#FF6B6B"},
                ]
            }
        }