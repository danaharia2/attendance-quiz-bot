# quiz_database.py
import json
import os
import sys
from typing import List, Dict, Any

# Tambahkan path untuk import quiz_models
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from quiz_models import Question
    print("✅ quiz_models imported successfully in quiz_database")
except ImportError as e:
    print(f"❌ Failed to import quiz_models in quiz_database: {e}")
    
    # Fallback Question class
    from datetime import datetime
    class Question:
        def __init__(self, question, correct_answers, category="umum", difficulty="medium"):
            self.question = question
            self.correct_answers = correct_answers
            self.category = category
            self.difficulty = difficulty
        
        def to_dict(self):
            return {
                "question": self.question,
                "correct_answers": self.correct_answers,
                "category": self.category,
                "difficulty": self.difficulty
            }
        
        @classmethod
        def from_dict(cls, data):
            return cls(
                question=data["question"],
                correct_answers=data["correct_answers"],
                category=data.get("category", "umum"),
                difficulty=data.get("difficulty", "medium")
            )

class QuizDatabase:
    def __init__(self, db_file: str = "quiz_database.json"):
        self.db_file = os.path.join(current_dir, db_file)
        print(f"🔧 Database file path: {self.db_file}")
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data dari file JSON"""
        try:
            if os.path.exists(self.db_file):
                print(f"📁 Loading database from: {self.db_file}")
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    question_count = len(data.get("questions", []))
                    print(f"✅ Loaded database with {question_count} questions")
                    return data
            else:
                print(f"📁 Database file not found, creating: {self.db_file}")
                default_data = {
                    "questions": [],
                    "categories": {
                        "bahasa_rusia": "Bahasa Rusia",
                        "umum": "Umum",
                        "geografi": "Geografi", 
                        "sains": "Sains"
                    }
                }
                self._save_data(default_data)
                return default_data
        except Exception as e:
            print(f"❌ Error loading database: {e}")
            return {"questions": [], "categories": {}}
    
    def _save_data(self, data: Dict[str, Any]):
        """Simpan data ke file JSON"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved database with {len(data.get('questions', []))} questions")
        except Exception as e:
            print(f"❌ Error saving database: {e}")
    
    def get_all_questions(self) -> List[Question]:
        """Dapatkan semua pertanyaan sebagai Question objects"""
        questions = []
        for q_data in self.data.get("questions", []):
            try:
                questions.append(Question.from_dict(q_data))
            except Exception as e:
                print(f"❌ Error loading question: {e}")
        return questions
    
    def add_question(self, question: str, correct_answers: List[str], 
                    category: str = "umum", difficulty: str = "medium") -> bool:
        """Tambah pertanyaan baru"""
        try:
            new_question = Question(
                question=question,
                correct_answers=correct_answers,
                category=category,
                difficulty=difficulty
            )
            
            self.data["questions"].append(new_question.to_dict())
            self._save_data(self.data)
            return True
        except Exception as e:
            print(f"❌ Error adding question: {e}")
            return False
    
    def get_categories(self) -> Dict[str, str]:
        """Dapatkan daftar kategori"""
        return self.data.get("categories", {})
    
    def get_question_count(self) -> int:
        """Dapatkan jumlah total pertanyaan"""
        return len(self.data.get("questions", []))
    
    def get_question_count_by_category(self) -> Dict[str, int]:
        """Dapatkan jumlah pertanyaan per kategori"""
        count_dict = {}
        for question_data in self.data.get("questions", []):
            category = question_data.get("category", "umum")
            count_dict[category] = count_dict.get(category, 0) + 1
        return count_dict

# Instance global
quiz_db = QuizDatabase()
print("✅ quiz_database initialized successfully")