"""CLI interface for the medical dictation tool."""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel

from .llm_extractor import LLMExtractor
from .transcription import AudioTranscriber

# Load environment variables
load_dotenv()

app = typer.Typer(
    name="medical-cli",
    help="Transcribe and analyze German medical dictations",
    add_completion=False,
)
console = Console()


@app.command()
def process(
    audio_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the audio file (WAV, MP3, M4A, or FLAC)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path for JSON result (default: stdout)",
    ),
    model_size: str = typer.Option(
        "medium",
        "--model-size",
        "-m",
        help="Whisper model size (tiny, base, small, medium, large-v2, large-v3)",
    ),
    llm_model: str = typer.Option(
        "gpt-4o-mini",
        "--llm-model",
        "-l",
        help="LLM model to use (e.g., gpt-4o-mini, gpt-4o)",
    ),
    llm_base_url: Optional[str] = typer.Option(
        None,
        "--llm-base-url",
        help="Custom LLM base URL (for Ollama or other OpenAI-compatible APIs)",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        envvar="OPENAI_API_KEY",
        help="OpenAI API key (or set OPENAI_API_KEY env var)",
    ),
    device: str = typer.Option(
        "cpu",
        "--device",
        help="Device for Whisper model (cpu, cuda, auto)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
) -> None:
    """
    Process a German medical audio dictation.

    Transcribes the audio file and extracts structured clinical information.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Display header
        console.print(
            Panel.fit(
                "[bold cyan]Medical Dictation Analyzer[/bold cyan]\n"
                "Transcribe & Extract Clinical Data",
                border_style="cyan",
            )
        )

        # Step 1: Transcribe audio
        console.print("\n[bold]Step 1: Audio Transcription[/bold]")
        transcriber = AudioTranscriber(
            model_size=model_size,
            device=device,
            compute_type="int8",
        )
        transcript = transcriber.transcribe(audio_file, language="de")

        console.print(f"\n[bold]Transcript:[/bold]\n{transcript}\n")

        # Step 2: Extract structured data
        console.print("[bold]Step 2: Clinical Data Extraction[/bold]")
        extractor = LLMExtractor(
            api_key=api_key,
            model=llm_model,
            base_url=llm_base_url,
        )
        clinical_summary = extractor.extract_with_fallback(transcript)

        # Convert to JSON
        result = clinical_summary.model_dump(mode="json", exclude_none=True)

        # Output result
        console.print("\n[bold]Step 3: Results[/bold]")

        if output:
            output.write_text(json.dumps(result, ensure_ascii=False, indent=2))
            console.print(f"[green]✓ Results saved to: {output}[/green]")
        else:
            # Display to console with Rich formatting
            console.print(
                Panel(
                    JSON(json.dumps(result, ensure_ascii=False)),
                    title="Clinical Summary (JSON)",
                    border_style="green",
                )
            )

        console.print("\n[bold green]✓ Processing complete![/bold green]")

    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Processing interrupted by user[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(
            f"[bold red]Unexpected error:[/bold red] {e}",
            file=sys.stderr,
        )
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    console.print(f"Medical Dictation CLI v{__version__}")


if __name__ == "__main__":
    app()

