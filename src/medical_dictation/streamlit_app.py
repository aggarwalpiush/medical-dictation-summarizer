"""Streamlit demo for the medical dictation tool."""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

# Add src directory to path to allow imports when running directly
current_file = Path(__file__).resolve()
src_dir = current_file.parents[1]
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))

from medical_dictation.llm_extractor import LLMExtractor
from medical_dictation.transcription import AudioTranscriber

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Medical Dictation Analyzer",
    page_icon="🏥",
    layout="wide",
)


def main() -> None:
    """Main entry point for the Streamlit app."""
    st.title("🏥 Medical Dictation Analyzer")
    st.markdown(
        """
        Upload a German medical dictation (audio) to transcribe it and extract structured clinical data.
        """
    )

    # Sidebar Configuration
    with st.sidebar:
        st.header("Settings")

        # API Key handling
        env_api_key = os.getenv("OPENAI_API_KEY")
        api_key = st.text_input(
            "OpenAI API Key",
            value=env_api_key if env_api_key else "",
            type="password",
            help="Required for the LLM extraction step.",
        )

        st.divider()

        # Whisper Settings
        st.subheader("Transcription (Whisper)")
        model_size = st.selectbox(
            "Model Size",
            options=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
            index=3,  # Default to medium
            help="Larger models are more accurate but slower.",
        )
        device = st.selectbox(
            "Device",
            options=["cpu", "cuda", "auto"],
            index=2,  # Default to auto
        )

        st.divider()

        # LLM Settings
        st.subheader("Extraction (LLM)")
        llm_model = st.selectbox(
            "Model",
            options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0,
        )
        llm_base_url = st.text_input(
            "Base URL (Optional)",
            value="",
            help="Custom base URL for OpenAI-compatible APIs (e.g. Ollama)",
        )

    # Main Content
    uploaded_file = st.file_uploader(
        "Upload Audio File", type=["wav", "mp3", "m4a", "flac"]
    )

    if uploaded_file:
        # Display audio player
        st.audio(uploaded_file)

        if st.button("Process Dictation", type="primary"):
            if not api_key and not llm_base_url:
                st.warning("⚠ Please provide an OpenAI API Key or a Custom Base URL.")
                return

            process_audio(
                uploaded_file,
                api_key,
                model_size,
                device,
                llm_model,
                llm_base_url if llm_base_url else None,
            )


def process_audio(
    uploaded_file,
    api_key: Optional[str],
    model_size: str,
    device: str,
    llm_model: str,
    llm_base_url: Optional[str],
) -> None:
    """Process the uploaded audio file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(uploaded_file.name).suffix
    ) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = Path(tmp_file.name)

    try:
        # 1. Transcription
        st.info("🎙️ Transcribing audio... This may take a while depending on model size.")
        
        with st.spinner("Running Whisper..."):
            transcriber = AudioTranscriber(
                model_size=model_size,
                device=device,
                compute_type="int8",
            )
            transcript = transcriber.transcribe(tmp_path, language="de")
        
        st.success("Transcription complete!")
        
        with st.expander("View Transcript", expanded=True):
            st.text_area("Transcript", transcript, height=200)

        # 2. Extraction
        st.info("🧠 Extracting clinical data with LLM...")
        
        with st.spinner(f"Querying {llm_model}..."):
            extractor = LLMExtractor(
                api_key=api_key,
                model=llm_model,
                base_url=llm_base_url,
            )
            clinical_summary = extractor.extract_with_fallback(transcript)
            
        st.success("Extraction complete!")

        # 3. Results
        result_json = clinical_summary.model_dump(mode="json", exclude_none=True)
        
        st.subheader("Clinical Summary")
        
        tab1, tab2 = st.tabs(["Structured View", "JSON Source"])
        
        with tab1:
            st.json(result_json, expanded=True)
            
        with tab2:
            st.code(json.dumps(result_json, indent=2, ensure_ascii=False), language="json")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        # st.exception(e) # Uncomment for debugging
    finally:
        # Cleanup
        if tmp_path.exists():
            os.unlink(tmp_path)


if __name__ == "__main__":
    main()