from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    user_id: str
    email: str
    name: str
    experience_level: Optional[str] = None
    hardware_ownership: Optional[str] = None
    preferred_language: Optional[str] = None
    sign_up_date: Optional[datetime] = None
    last_login_date: Optional[datetime] = None

class UserPreference(BaseModel):
    preference_id: str
    user_id: str
    preference_type: str
    chapter_id: Optional[str] = None
    value: str