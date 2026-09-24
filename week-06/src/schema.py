from pydantic import BaseModel
from enum import Enum

class CanonicalTitle(str, Enum):
    SOFTWARE_ENGINEER = "Software Engineer"
    SENIOR_SOFTWARE_ENGINEER = "Senior Software Engineer"
    FRONTEND_DEVELOPER = "Frontend Developer"
    BACKEND_DEVELOPER = "Backend Developer"
    FULL_STACK_DEVELOPER = "Full Stack Developer"
    DATA_SCIENTIST = "Data Scientist"
    DATA_ENGINEER = "Data Engineer"
    PRODUCT_MANAGER = "Product Manager"
    DEVOPS_ENGINEER = "DevOps Engineer"
    QA_ENGINEER = "QA Engineer"
    OTHER = "Other"

class NormalizeOutput(BaseModel):
    canonical_title: CanonicalTitle
    confidence: float
    reason: str