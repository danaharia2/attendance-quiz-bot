# quiz_models.py
from datetime import datetime
from typing import List, Optional

class Question:
    def __init__(self, question: str, correct_answers: List[str], 
                 category: str = "umum", difficulty: str = "medium",
                 options: Optional[List[str]] = None):
        self.question = question
        self.correct_answers = correct_answers
        self.options = options or []
        self.category = category
        self.difficulty = difficulty
        self.created_by = None
        self.created_at = datetime.now()
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return {
            "question": self.question,
            "correct_answers": self.correct_answers,
            "options": self.options,
            "category": self.category,
            "difficulty": self.difficulty,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        question = cls(
            question=data["question"],
            correct_answers=data["correct_answers"],
            category=data.get("category", "umum"),
            difficulty=data.get("difficulty", "medium"),
            options=data.get("options", [])
        )
        if data.get("created_by"):
            question.created_by = data["created_by"]
        return question

print("✅ quiz_models.py loaded successfully")