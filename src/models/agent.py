from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Subagent(BaseModel):
    agent_id: str
    name: str
    description: str
    capabilities: List[str]

class AgentSkill(BaseModel):
    skill_id: str
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None