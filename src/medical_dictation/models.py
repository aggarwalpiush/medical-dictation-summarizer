"""Data models for structured clinical information."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ClinicalSummary(BaseModel):
    """Structured clinical summary extracted from medical dictation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patient_complaint": "Kopfschmerzen und Schwindel seit 3 Tagen",
                "findings": [
                    "Blutdruck 140/90 mmHg",
                    "Neurologische Untersuchung unauffällig",
                ],
                "diagnosis": "Spannungskopfschmerz",
                "secondary_diagnoses": ["Arterielle Hypertonie"],
                "next_steps": [
                    "Blutdruckkontrolle in 2 Wochen",
                    "Bei Verschlechterung neurologische Abklärung",
                ],
                "medications": ["Ibuprofen 400mg bei Bedarf"],
                "additional_notes": "Patient ist beruflich stark belastet",
            }
        }
    )

    patient_complaint: Optional[str] = Field(
        None,
        description="The patient's chief complaint or reason for visit",
    )
    findings: Optional[List[str]] = Field(
        None,
        description="Clinical findings and observations from examination",
    )
    diagnosis: Optional[str] = Field(
        None,
        description="Primary diagnosis or diagnostic impression",
    )
    secondary_diagnoses: Optional[List[str]] = Field(
        None,
        description="Additional or differential diagnoses",
    )
    next_steps: Optional[List[str]] = Field(
        None,
        description="Recommended next steps, treatment plan, or follow-up",
    )
    medications: Optional[List[str]] = Field(
        None,
        description="Medications mentioned (prescribed or current)",
    )
    additional_notes: Optional[str] = Field(
        None,
        description="Any additional relevant information",
    )


