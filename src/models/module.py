from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Module(BaseModel):
    module_id: str
    textbook_id: str
    title: str
    order: int