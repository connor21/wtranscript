# Media Transcription App

A Streamlit-based application for transcribing audio and video files using OpenAI's Whisper model via faster-whisper.

## Features

- **Multiple Format Support**: mp3, wav, m4a, mp4, mov
- **Quality Selection**: Choose between low (faster) and high (better quality) transcription models
- **Partial Transcription**: Optionally transcribe only a specific time range
- **Copy to Clipboard**: Easy one-click copy of transcript text
- **Abort Support**: Cancel running transcriptions
- **Automatic Cleanup**: Temporary files are automatically deleted after success, abort, or failure

## Prerequisites

### System Dependencies

- **Python 3.8+**
- **ffmpeg**: Required for media processing

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

### Option 1: Docker (Recommended)

1. Clone or download this repository

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

3. Open your browser at `http://localhost:8501`

**Or build manually:**
```bash
# Build the image
docker build -t transcription-app .

# Run the container
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
- Use "Low (faster)" quality option
- Transcribe shorter segments using partial transcription
- Consider using a machine with better CPU/GPU

### Model download on first run
The first time you use each quality setting, faster-whisper will download the model. This is a one-time download.

### File size too large
If you get an upload error, increase the `maxUploadSize` in `.streamlit/config.toml` (see Configuration section).

## Technical Details

- **Framework**: Streamlit
- **Transcription Engine**: faster-whisper
- **Media Processing**: ffmpeg
- **Supported Formats**: mp3, wav, m4a, mp4, mov

## License

This project is provided as-is for transcription purposes.
