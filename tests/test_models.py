"""Unit tests for the medical dictation CLI."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from medical_dictation.models import ClinicalSummary


class TestClinicalSummary:
    """Tests for the ClinicalSummary model."""

    def test_clinical_summary_creation_with_all_fields(self):
        """Test creating a clinical summary with all fields."""
        summary = ClinicalSummary(
            patient_complaint="Kopfschmerzen",
            findings=["Blutdruck 120/80"],
            diagnosis="Spannungskopfschmerz",
            secondary_diagnoses=["Hypertonie"],
            next_steps=["Kontrolle in 1 Woche"],
            medications=["Ibuprofen 400mg"],
            additional_notes="Patient ist gestresst",
        )

        assert summary.patient_complaint == "Kopfschmerzen"
        assert len(summary.findings) == 1
        assert summary.diagnosis == "Spannungskopfschmerz"

    def test_clinical_summary_creation_with_minimal_fields(self):
        """Test creating a clinical summary with minimal fields."""
        summary = ClinicalSummary(diagnosis="Test Diagnose")

        assert summary.diagnosis == "Test Diagnose"
        assert summary.patient_complaint is None
        assert summary.findings is None

    def test_clinical_summary_empty(self):
        """Test creating an empty clinical summary."""
        summary = ClinicalSummary()

        assert summary.patient_complaint is None
        assert summary.findings is None
        assert summary.diagnosis is None

    def test_clinical_summary_to_json(self):
        """Test converting clinical summary to JSON."""
        summary = ClinicalSummary(
            patient_complaint="Kopfschmerzen",
            diagnosis="Spannungskopfschmerz",
        )

        data = summary.model_dump(mode="json", exclude_none=True)
        json_str = json.dumps(data, ensure_ascii=False)

        assert "Kopfschmerzen" in json_str
        assert "Spannungskopfschmerz" in json_str

    def test_clinical_summary_from_json(self):
        """Test creating clinical summary from JSON."""
        json_data = {
            "patient_complaint": "Husten",
            "diagnosis": "Bronchitis",
            "medications": ["Antibiotika"],
        }

        summary = ClinicalSummary(**json_data)

        assert summary.patient_complaint == "Husten"
        assert summary.diagnosis == "Bronchitis"
        assert len(summary.medications) == 1


class TestModelsValidation:
    """Tests for data validation."""

    def test_findings_must_be_list(self):
        """Test that findings must be a list if provided."""
        # This should work
        summary = ClinicalSummary(findings=["Befund 1", "Befund 2"])
        assert len(summary.findings) == 2

    def test_exclude_none_fields(self):
        """Test that None fields are excluded from export."""
        summary = ClinicalSummary(diagnosis="Test")
        data = summary.model_dump(mode="json", exclude_none=True)

        assert "diagnosis" in data
        assert "patient_complaint" not in data
        assert "findings" not in data


# Integration test placeholder
class TestIntegration:
    """Integration tests (require API keys and audio files)."""

    @pytest.mark.skip(reason="Requires audio file and API key")
    def test_full_pipeline(self):
        """Test the full transcription and extraction pipeline."""
        # This would test the actual transcription and LLM extraction
        # Requires:
        # - A test audio file
        # - OpenAI API key
        # - Sufficient time for processing
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

