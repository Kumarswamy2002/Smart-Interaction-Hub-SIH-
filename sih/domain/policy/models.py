from enum import Enum
from pydantic import BaseModel

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PolicyResult(BaseModel):
    allowed: bool
    risk_level: RiskLevel
    requires_approval: bool
    reason: str
