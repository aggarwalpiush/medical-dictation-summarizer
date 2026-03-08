"""LLM extraction module for extracting structured clinical data from transcripts."""

import json
import logging
import os
from typing import Optional

from openai import OpenAI
from rich.console import Console

from .models import ClinicalSummary

logger = logging.getLogger(__name__)
console = Console()


class LLMExtractor:
    """Extract structured clinical information from medical transcripts using LLM."""

    SYSTEM_PROMPT = """Du bist ein medizinischer Assistent, der aus deutschen medizinischen Diktaten strukturierte Informationen extrahiert.

Extrahiere aus dem folgenden medizinischen Diktat die relevanten klinischen Informationen und gib sie als JSON zurück.

Befolge diese Regeln:
1. Extrahiere nur Informationen, die explizit im Text erwähnt werden
2. Verwende die deutschen medizinischen Fachbegriffe aus dem Original
3. Wenn eine Information nicht vorhanden ist, setze das Feld auf null
4. Sei präzise und vollständig

Das JSON-Schema:
{
  "patient_complaint": "Beschwerden/Symptome des Patienten (string oder null)",
  "findings": "Liste der klinischen Befunde aus der Untersuchung (array oder null)",
  "diagnosis": "Hauptdiagnose (string oder null)",
  "secondary_diagnoses": "Weitere Diagnosen (array oder null)",
  "next_steps": "Weiteres Vorgehen, Therapie, Kontrollen (array oder null)",
  "medications": "Erwähnte Medikamente (array oder null)",
  "additional_notes": "Zusätzliche relevante Informationen (string oder null)"
}

Antworte NUR mit gültigem JSON, ohne zusätzliche Erklärungen."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
    ):
        """
        Initialize the LLM extractor.

        Args:
            api_key: OpenAI API key (or None to use env var)
            model: Model to use (gpt-4o-mini, gpt-4o, or local model name)
            base_url: Custom base URL (for local models like Ollama)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url

        if not self.api_key and not self.base_url:
            raise ValueError(
                "OpenAI API key must be provided via parameter or OPENAI_API_KEY env var"
            )

        # Initialize OpenAI client (compatible with Ollama and other OpenAI-compatible APIs)
        self.client = OpenAI(
            api_key=self.api_key or "dummy-key",  # Ollama doesn't need real key
            base_url=self.base_url,
        )

    def extract(self, transcript: str) -> ClinicalSummary:
        """
        Extract structured clinical information from a transcript.

        Args:
            transcript: The transcribed medical dictation text

        Returns:
            ClinicalSummary object with extracted information
        """
        console.print("[cyan]Extracting structured clinical data with LLM...[/cyan]")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Medizinisches Diktat:\n\n{transcript}",
                    },
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")

            # Parse JSON and validate with Pydantic
            data = json.loads(content)
            summary = ClinicalSummary(**data)

            console.print("[green]✓ Clinical data extracted successfully[/green]")

            return summary

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise RuntimeError(f"Invalid JSON response from LLM: {e}")
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            raise RuntimeError(f"Failed to extract clinical data: {e}")

    def extract_with_fallback(self, transcript: str) -> ClinicalSummary:
        """
        Extract with fallback to simpler prompt if JSON parsing fails.

        Args:
            transcript: The transcribed medical dictation text

        Returns:
            ClinicalSummary object
        """
        try:
            return self.extract(transcript)
        except RuntimeError as e:
            console.print(
                f"[yellow]⚠ Extraction failed, trying fallback approach: {e}[/yellow]"
            )

            # Fallback: try without response_format constraint
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Medizinisches Diktat:\n\n{transcript}",
                        },
                    ],
                    temperature=0.0,
                )

                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from LLM")

                # Try to extract JSON from response (might have extra text)
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    data = json.loads(json_str)
                    summary = ClinicalSummary(**data)
                    console.print("[green]✓ Clinical data extracted (fallback)[/green]")
                    return summary
                else:
                    raise ValueError("No JSON object found in response")

            except Exception as fallback_error:
                logger.error(f"Fallback extraction also failed: {fallback_error}")
                raise RuntimeError(
                    f"All extraction attempts failed: {fallback_error}"
                )

