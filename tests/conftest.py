"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_german_transcript():
    """Sample German medical transcript for testing."""
    return """
    Patient klagt über starke Kopfschmerzen seit drei Tagen.
    Die Schmerzen sind frontal lokalisiert und werden als drückend beschrieben.
    Blutdruck bei der Untersuchung: 135 über 85 mmHg.
    Neurologische Untersuchung ohne pathologischen Befund.
    Diagnose: Spannungskopfschmerz.
    Therapieempfehlung: Ibuprofen 400mg bei Bedarf.
    Kontrolle in einer Woche bei Persistenz der Beschwerden.
    """


@pytest.fixture
def expected_clinical_data():
    """Expected structured data from sample transcript."""
    return {
        "patient_complaint": "Starke Kopfschmerzen seit drei Tagen",
        "findings": [
            "Blutdruck 135/85 mmHg",
            "Neurologische Untersuchung ohne pathologischen Befund",
        ],
        "diagnosis": "Spannungskopfschmerz",
        "next_steps": [
            "Ibuprofen 400mg bei Bedarf",
            "Kontrolle in einer Woche bei Persistenz",
        ],
    }

