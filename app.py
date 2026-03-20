import streamlit as st
import os
import tempfile
import subprocess
from typing import Optional, Tuple
from faster_whisper import WhisperModel
import logging


SUPPORTED_FORMATS = ['mp3', 'wav', 'm4a', 'mp4', 'mov']
QUALITY_OPTIONS = {
    'Low (faster)': 'small',
    'High (better quality)': 'large-v3'
}

logging.basicConfig(level=logging.INFO)


def init_session_state():
    if 'uploaded_file_path' not in st.session_state:
        st.session_state.uploaded_file_path = None
    if 'uploaded_filename' not in st.session_state:
        st.session_state.uploaded_filename = None
    if 'transcript_text' not in st.session_state:
        st.session_state.transcript_text = None
    if 'status_message' not in st.session_state:
        st.session_state.status_message = ''
    if 'error_message' not in st.session_state:
        st.session_state.error_message = ''
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = None
    if 'segment_file_path' not in st.session_state:
        st.session_state.segment_file_path = None
    if 'start_transcription' not in st.session_state:
        st.session_state.start_transcription = False
    if 'transcription_params' not in st.session_state:
        st.session_state.transcription_params = None


def get_device_and_compute_type() -> Tuple[str, str]:
    """
    Detect available device and return optimal settings.
    Returns: (device, compute_type)
    """
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            logging.info(f"GPU detected: {gpu_name}")
            return "cuda", "float16"
    except ImportError:
        logging.info("PyTorch not available, using CPU")
    except Exception as e:
        logging.warning(f"Error checking GPU: {e}")
    
    logging.info("Using CPU")
    return "cpu", "int8"


def validate_ffmpeg() -> bool:
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_media_duration(file_path: str) -> Optional[float]:
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def validate_time_range(start: float, end: float, duration: Optional[float]) -> Tuple[bool, str]:
    if start < 0:
        return False, "Start time must be >= 0"
    if end <= start:
        return False, "End time must be > start time"
    if duration is not None and end > duration:
        return False, f"End time cannot exceed media duration ({duration:.2f}s)"
    return True, ""


def extract_segment(input_path: str, output_path: str, start: float, end: float) -> bool:
    try:
        duration = end - start
        subprocess.run(
            ['ffmpeg', '-i', input_path, '-ss', str(start), '-t', str(duration),
             '-c', 'copy', output_path, '-y'],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def cleanup_temp_files(uploaded_path=None, segment_path=None, temp_dir=None):
    if uploaded_path and os.path.exists(uploaded_path):
        try:
            os.remove(uploaded_path)
        except Exception:
            pass
    
    if segment_path and os.path.exists(segment_path):
        try:
            os.remove(segment_path)
        except Exception:
            pass
    
    if temp_dir and os.path.exists(temp_dir):
        try:
            if not os.listdir(temp_dir):
                os.rmdir(temp_dir)
        except Exception:
            pass


def run_transcription(file_path: str, model_size: str, uploaded_path: str, segment_path: Optional[str], temp_dir: str):
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    try:
        device, compute_type = get_device_and_compute_type()
        device_label = "GPU (CUDA)" if device == "cuda" else "CPU"
        status_placeholder.info(f"🔄 Loading model on {device_label}...")
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        status_placeholder.info("🎙️ Transcribing...")
        progress_bar.progress(30)
        
        segments, info = model.transcribe(file_path, beam_size=5)
        
        transcript_parts = []
        total_segments = 0
        
        for segment in segments:
            transcript_parts.append(segment.text)
            total_segments += 1
            if total_segments % 10 == 0:
                progress_bar.progress(min(30 + (total_segments * 2), 90))
        
        progress_bar.progress(100)
        transcript = ' '.join(transcript_parts).strip()
        
        status_placeholder.success("✅ Transcription complete!")
        st.session_state.transcript_text = transcript
        st.session_state.status_message = 'Done'
        
    except Exception as e:
        status_placeholder.error(f"❌ Transcription failed: {str(e)}")
        st.session_state.error_message = f"Error: {str(e)}"
        st.session_state.status_message = 'Failed'
    finally:
        cleanup_temp_files(uploaded_path, segment_path, temp_dir)
        progress_bar.empty()


def main():
    st.set_page_config(page_title="Media Transcription", layout="wide")
    
    init_session_state()
    
    st.title("🎙️ Media Transcription App")
    st.markdown("Upload a media file and transcribe it using Whisper AI")
    
    if not validate_ffmpeg():
        st.error("⚠️ **ffmpeg is not installed or not available on PATH.** Please install ffmpeg to use this app.")
        st.stop()
    
    uploaded_file = st.file_uploader(
        "Upload media file",
        type=SUPPORTED_FORMATS,
        help=f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
    )
    
    if uploaded_file is not None:
        if st.session_state.uploaded_filename != uploaded_file.name:
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.transcript_text = None
            st.session_state.status_message = ''
            st.session_state.error_message = ''
            
            if st.session_state.temp_dir is None:
                st.session_state.temp_dir = tempfile.mkdtemp()
            
            file_path = os.path.join(st.session_state.temp_dir, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.uploaded_file_path = file_path
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        st.divider()
        
        quality_choice = st.radio(
            "Transcription Quality",
            options=list(QUALITY_OPTIONS.keys()),
            index=0,
            horizontal=True
        )
        
        model_size = QUALITY_OPTIONS[quality_choice]
        
        st.divider()
        
        use_partial = st.checkbox("Transcribe partial range")
        
        start_time = 0.0
        end_time = None
        time_valid = True
        validation_error = ""
        
        if use_partial:
            duration = get_media_duration(st.session_state.uploaded_file_path)
            
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.number_input(
                    "Start time (seconds)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    format="%.2f"
                )
            with col2:
                default_end = duration if duration else 60.0
                end_time = st.number_input(
                    "End time (seconds)",
                    min_value=0.0,
                    value=default_end,
                    step=1.0,
                    format="%.2f"
                )
            
            time_valid, validation_error = validate_time_range(start_time, end_time, duration)
            
            if not time_valid:
                st.error(f"⚠️ {validation_error}")
            elif duration:
                st.info(f"ℹ️ Media duration: {duration:.2f}s | Selected range: {end_time - start_time:.2f}s")
        
        st.divider()
        
        if st.button("▶️ Transcribe", disabled=not time_valid, use_container_width=True, type="primary"):
            st.session_state.status_message = ''
            st.session_state.error_message = ''
            st.session_state.transcript_text = None
            st.session_state.segment_file_path = None
            
            file_to_transcribe = st.session_state.uploaded_file_path
            segment_path = None
            
            if use_partial:
                with st.spinner('Extracting segment...'):
                    segment_path = os.path.join(
                        st.session_state.temp_dir,
                        f"segment_{uploaded_file.name}"
                    )
                    if extract_segment(st.session_state.uploaded_file_path, segment_path, start_time, end_time):
                        file_to_transcribe = segment_path
                        st.session_state.segment_file_path = segment_path
                    else:
                        st.error('❌ Failed to extract segment')
                        cleanup_temp_files(st.session_state.uploaded_file_path, segment_path, st.session_state.temp_dir)
                        st.stop()
            
            run_transcription(
                file_to_transcribe, 
                model_size,
                st.session_state.uploaded_file_path,
                segment_path,
                st.session_state.temp_dir
            )
        
        if st.session_state.error_message:
            st.error(st.session_state.error_message)
        
        if st.session_state.transcript_text:
            st.divider()
            st.subheader("📝 Transcript")
            
            st.text_area(
                "Transcript text",
                value=st.session_state.transcript_text,
                height=300,
                label_visibility="collapsed"
            )
            
            st.download_button(
                label="📥 Download transcript",
                data=st.session_state.transcript_text,
                file_name="transcript.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    else:
        st.info("👆 Please upload a media file to begin")


if __name__ == "__main__":
    main()
