# Medical Dictation CLI

A Python CLI application that transcribes German medical dictations from audio files and extracts structured clinical 
summaries.


## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key (or local LLM setup with Ollama)
- ffmpeg (for audio processing)

### Installation with uv (Local)

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
Note: You might need to either restart your session or run following command:

```bash
  source $HOME/.local/bin/env
```

2. **Clone or navigate to the project**:
   ```bash
   cd medical-dictation-summarizer
   ```
   
Tip: Create uv environment before installation. To do so, use following commands:

```bash
    uv venv --python 3.11
    source .venv/bin/activate
```

3. **Install dependencies**:
   ```bash
   uv pip install -e .
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   # if you want to use local LLM instead of OpenAI, ollama models can be used, please comment the .env.example 
   # accordingly.
   ```

### Installation with Docker

Assuming: Docker is pre-installed.

1. **Build the Docker image**:
   ```bash
   docker build -t medical-dictation-cli .
   ```

2. **Run the container** (see usage examples below)

## Usage

### Local Usage (uv)

Process an audio file:

```bash
python -m medical_dictation.cli process path/to/audio.wav
```

Save output to a file:

```bash
python -m medical_dictation.cli process audio.mp3 --output result.json
```

Use a different Whisper model size:

```bash
python -m medical_dictation.cli process audio.wav --model-size large-v3
```

Use a specific LLM model:

```bash
python -m medical_dictation.cli process audio.wav --llm-model gpt-4o
```

### Docker Usage

Process an audio file using Docker:

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=your-api-key-here \
  medical-dictation-cli process /app/data/audio.wav
```

Save output to a file:

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=your-api-key-here \
  medical-dictation-cli process /app/data/audio.wav --output /app/data/result.json
```

Use with environment file:

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  medical-dictation-cli process /app/data/audio.wav
```

### Using Local LLM (Ollama)

If you want to use a local LLM instead of OpenAI API:

1. **Install and start Ollama**:
   ```bash
   # Install from https://ollama.ai 
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3
   ollama serve
   ```

Now in another terminal make sure you activate the virtual environment.

2. **Run with custom LLM settings**:
   ```bash
   python -m medical_dictation.cli process audio.wav \
     --llm-base-url http://localhost:11434/v1 \
     --llm-model llama3
   ```

### Streamlit Web Interface

To run the interactive web demo:

```bash
  streamlit run src/medical_dictation/streamlit_app.py
```

Note: Please make sure streamlit is installed. If not please use the following command:

```bash
  uv pip install streamlit
```

## Command-Line Options

```
process [OPTIONS] AUDIO_FILE

Arguments:
  AUDIO_FILE              Path to the audio file (WAV, MP3, M4A, or FLAC) [required]

Options:
  -o, --output PATH       Output file path for JSON result (default: stdout)
  -m, --model-size TEXT   Whisper model size: tiny, base, small, medium, large-v2, large-v3
                          [default: medium]
  -l, --llm-model TEXT    LLM model to use [default: gpt-4o-mini]
  --llm-base-url TEXT     Custom LLM base URL (for Ollama or other OpenAI-compatible APIs)
  --api-key TEXT          OpenAI API key (or set OPENAI_API_KEY env var)
  --device TEXT           Device for Whisper model: cpu, cuda, auto [default: cpu]
  -v, --verbose           Enable verbose logging
  --help                  Show this message and exit
```

## Output Format

The application returns a JSON object with the following structure. For example:

```json
{
  "patient_complaint": "Kopfschmerzen und Schwindel seit 3 Tagen",
  "findings": [
    "Blutdruck 140/90 mmHg",
    "Neurologische Untersuchung unauffällig"
  ],
  "diagnosis": "Spannungskopfschmerz",
  "secondary_diagnoses": [
    "Arterielle Hypertonie"
  ],
  "next_steps": [
    "Blutdruckkontrolle in 2 Wochen",
    "Bei Verschlechterung neurologische Abklärung"
  ],
  "medications": [
    "Ibuprofen 400mg bei Bedarf"
  ],
  "additional_notes": "Patient ist beruflich stark belastet"
}
```

All fields are optional and will be omitted if no relevant information is found in the dictation.

## Project Structure

```
python-project-learning/
├── src/
│   └── medical_dictation/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # CLI interface (Typer)
│       ├── transcription.py     # Audio transcription (faster-whisper)
│       ├── llm_extractor.py     # LLM-based extraction
│       └── models.py            # Pydantic data models
├── pyproject.toml               # Project configuration (uv)
├── Dockerfile                   # Docker image definition
├── .dockerignore                # Docker ignore file
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore file
└── README.md                    # This file
```

## Model Sizes

The application uses faster-whisper for transcription. Model sizes and their characteristics:

| Model    | Parameters | Required RAM | Relative Speed | Quality |
|----------|-----------|--------------|----------------|---------|
| tiny     | 39 M      | ~1 GB        | ~10x           | Lowest  |
| base     | 74 M      | ~1 GB        | ~7x            | Low     |
| small    | 244 M     | ~2 GB        | ~4x            | Medium  |
| medium   | 769 M     | ~5 GB        | ~2x            | Good    |
| large-v2 | 1550 M    | ~10 GB       | 1x             | Best    |
| large-v3 | 1550 M    | ~10 GB       | 1x             | Best    |

**Recommendation**: Use `medium` (default) for a good balance between speed and accuracy. Use `large-v3` for best results with medical terminology.

## LLM Options

### OpenAI API (Recommended)
- **gpt-4o-mini** (default): Fast, cost-effective, good quality (default)
- **gpt-4o**: Best quality, slower, more expensive

### Local Models (via Ollama)
- **llama3**: Good open-source alternative
- **mixtral**: Excellent for structured extraction
- **gemma2**: Smaller, faster option

Please note that:

1. **First run is slower**: The Whisper model needs to be downloaded (cached afterward)
2. **Use GPU if available**: Add `--device cuda` for 5-10x speedup
3. **Optimize model size**: Balance speed vs. accuracy based on your needs
4. **Batch processing**: Process multiple files in sequence for efficiency