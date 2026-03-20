# Media Transcription App

A Streamlit-based application for transcribing audio and video files using OpenAI's Whisper model via faster-whisper.

**🚀 GPU-Accelerated**: Automatically detects and utilizes NVIDIA GPUs for significantly faster transcription (5-10x speedup).

## Features

- **GPU Acceleration**: Automatic NVIDIA GPU detection and utilization for faster transcription
- **CPU Fallback**: Seamlessly falls back to CPU if no GPU is available
- **Multiple Format Support**: mp3, wav, m4a, mp4, mov
- **Quality Selection**: Choose between low (faster) and high (better quality) transcription models
- **Partial Transcription**: Optionally transcribe only a specific time range
- **Copy to Clipboard**: Easy one-click copy of transcript text
- **Abort Support**: Cancel running transcriptions
- **Automatic Cleanup**: Temporary files are automatically deleted after success, abort, or failure

## Prerequisites

### System Dependencies

- **Python 3.11+**
- **ffmpeg**: Required for media processing

### GPU Support (Optional but Recommended)

For GPU-accelerated transcription, you need:

- **NVIDIA GPU** with CUDA support (Compute Capability 3.5+)
- **NVIDIA GPU Drivers** (version 450.80.02 or higher)
- **CUDA Toolkit** (12.1 or compatible version)
- **Docker with NVIDIA Container Toolkit** (for Docker deployment)

#### Installing NVIDIA Container Toolkit (for Docker)

**Ubuntu/Debian:**
```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-container-toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Restart Docker
sudo systemctl restart docker
```

**Verify GPU access:**
```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

#### Installing ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## Installation

### Option 1: Docker with GPU Support (Recommended)

1. Clone or download this repository

2. Ensure NVIDIA Container Toolkit is installed (see Prerequisites)

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

4. Open your browser at `http://localhost:8501`

5. Check logs to verify GPU detection:
```bash
docker-compose logs -f
# Look for: "GPU detected: [Your GPU Name]"
```

**Or build manually:**
```bash
# Build the image
docker build -t transcription-app .

# Run with GPU support
docker run --gpus all -p 8501:8501 -v model-cache:/root/.cache/huggingface transcription-app

# Run CPU-only (fallback)
docker run -p 8501:8501 -v model-cache:/root/.cache/huggingface transcription-app
```

### Option 2: Local Python Installation

1. Clone or download this repository

2. Create and activate a Python virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

**For GPU support (local installation):**
```bash
# Install PyTorch with CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Verify GPU is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Usage

### Docker

```bash
# Start the app
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the app
docker-compose down
```

### Local Installation

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate
```

2. Start the Streamlit app:
```bash
streamlit run app.py
```

3. Open your browser (usually auto-opens to `http://localhost:8501`)

### Workflow

Follow these steps:
   - Upload a media file (mp3, wav, m4a, mp4, or mov)
   - Select transcription quality (Low/High)
   - Optionally enable partial transcription and set time range
   - Click "Transcribe" to start
   - View and copy the transcript when complete

## Transcription Quality Options

- **Low (faster)**: Uses `small` model - faster processing, good accuracy
- **High (better quality)**: Uses `large-v3` model - slower processing, best accuracy

## Partial Transcription

Enable "Transcribe partial range" to transcribe only a specific segment:
- Set start time in seconds
- Set end time in seconds
- The app validates that end > start and end ≤ media duration

## Abort Functionality

Click the "Abort" button during transcription to:
- Stop the running transcription
- Clean up temporary files
- Return to ready state

## File Cleanup

The app automatically removes temporary files after:
- Successful transcription
- Aborted transcription
- Failed transcription

## Configuration

### Upload File Size Limit

The default upload size limit is **1000 MB (1 GB)**. To change this:

1. Edit `.streamlit/config.toml`
2. Modify the `maxUploadSize` value (in MB):

```toml
[server]
maxUploadSize = 2000  # Set to 2 GB
```

Common size limits:
- **500** = 500 MB
- **1000** = 1 GB (default)
- **2000** = 2 GB
- **5000** = 5 GB

## Troubleshooting

### "ffmpeg is not installed" error
Ensure ffmpeg is installed and available on your system PATH.

### Slow transcription
- **Enable GPU**: Ensure NVIDIA GPU is available and properly configured (5-10x faster)
- Use "Low (faster)" quality option
- Transcribe shorter segments using partial transcription
- Check logs to verify GPU is being used: Look for "Loading model on GPU (CUDA)"

### GPU not detected
- Verify NVIDIA drivers are installed: `nvidia-smi`
- For Docker: Ensure nvidia-container-toolkit is installed
- For local: Install PyTorch with CUDA support (see Installation)
- Check Docker Compose includes GPU configuration
- Restart Docker daemon after installing nvidia-container-toolkit

### Model download on first run
The first time you use each quality setting, faster-whisper will download the model. This is a one-time download.

### File size too large
If you get an upload error, increase the `maxUploadSize` in `.streamlit/config.toml` (see Configuration section).

## Technical Details

- **Framework**: Streamlit
- **Transcription Engine**: faster-whisper
- **Media Processing**: ffmpeg
- **GPU Acceleration**: PyTorch with CUDA 12.1
- **Supported Formats**: mp3, wav, m4a, mp4, mov
- **Compute Types**:
  - GPU: `float16` (optimal performance)
  - CPU: `int8` (optimized for CPU inference)

## Performance Comparison

| Hardware | Model Size | 10-min Audio | 60-min Audio |
|----------|-----------|--------------|---------------|
| CPU (8-core) | small | ~2-3 min | ~15-20 min |
| CPU (8-core) | large-v3 | ~8-12 min | ~50-70 min |
| GPU (RTX 3060) | small | ~20-30 sec | ~2-3 min |
| GPU (RTX 3060) | large-v3 | ~1-2 min | ~8-12 min |

*Times are approximate and vary based on audio complexity and hardware specifications.*

## License

This project is provided as-is for transcription purposes.
