from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Chapter(BaseModel):
    chapter_id: str
    module_id: str
    title: str
    order: int
    content: str
    learning_outcomes: str
    key_takeaways: str
    quiz_data: Optional[str] = None
    urdu_content: Optional[str] = None