from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

class mail_eval(BaseModel):
    category: Literal[
        "assignment",
        "announcement",
        "exam",
        "event",
        "administrative",
        "other"
    ]
    course: str | None=None
    title: str=Field(
        description= "A concise title describing the email's main subject"
    )
    summary: str=Field(
        description="A brief and concise summary of the important information"
    )
    action_required: bool
    deadline: str | None=Field(
        description="Explicit submission or action deadline in strict 'YYYY-MM-DD' ISO format. If no explicit deadline, set to null.",
        default=None
    )
    confidence_score: float = Field(
        description= "Confidence in overall analysis between 0 to 1",
        ge=0.0,
        le=1.0
    )
    priority: Literal[
        "high",
        "medium",
        "low"
    ]