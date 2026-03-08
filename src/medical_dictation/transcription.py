"""Audio transcription module using faster-whisper for German medical dictations."""

import logging
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

logger = logging.getLogger(__name__)
console = Console()


class AudioTranscriber:
    """Transcribe audio files using faster-whisper optimized for German language."""

    def __init__(
        self,
        model_size: str = "medium",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        """
        Initialize the transcriber with a Whisper model.

        Args:
            model_size: Model size (tiny, base, small, medium, large-v2, large-v3)
            device: Device to run on (cpu, cuda, auto)
            compute_type: Computation precision (int8, float16, float32)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model: Optional[WhisperModel] = None

    def load_model(self) -> None:
        """Load the Whisper model."""
        console.print(f"[cyan]Loading Whisper model ({self.model_size})...[/cyan]")
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            console.print("[green]✓ Model loaded successfully[/green]")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}")

    def transcribe(
        self,
        audio_path: Path,
        language: str = "de",
        initial_prompt: Optional[str] = None,
    ) -> str:
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to the audio file (WAV or MP3)
            language: Language code (default: "de" for German)
            initial_prompt: Optional prompt to guide transcription

        Returns:
            Transcribed text
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if not audio_path.suffix.lower() in [".wav", ".mp3", ".m4a", ".flac"]:
            raise ValueError(f"Unsupported audio format: {audio_path.suffix}")

        if self.model is None:
            self.load_model()

        console.print(f"[cyan]Transcribing audio file: {audio_path.name}[/cyan]")

        try:
            # Define prompt to help with medical terminology
            if initial_prompt is None:
                initial_prompt = (
                    "Dies ist eine medizinische Diktat mit Fachbegriffen. "
                    "Patient, Diagnose, Befund, Anamnese, Therapie."
                )

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Transcribing...", total=None)

                segments, info = self.model.transcribe(
                    str(audio_path),
                    language=language,
                    initial_prompt=initial_prompt,
                    beam_size=5,
                    best_of=5,
                    temperature=0.0,
                    vad_filter=True,  # Voice activity detection
                    vad_parameters=dict(
                        min_silence_duration_ms=500
                    ),  # Remove long silences
                )

                # Combine all segments into full transcript
                transcript_parts = []
                for segment in segments:
                    transcript_parts.append(segment.text.strip())

            transcript = " ".join(transcript_parts)

            console.print(
                f"[green]✓ Transcription complete[/green] "
                f"(detected language: {info.language}, "
                f"probability: {info.language_probability:.2f})"
            )

            return transcript

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Failed to transcribe audio: {e}")

