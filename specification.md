# Streamlit Media Transcription App Specification

This specification defines a single-page Streamlit app that transcribes uploaded media files, supports low/high quality model selection, supports optional partial transcription by time range, and returns transcript text with copy-to-clipboard support.

## 1) Scope

- Framework: `streamlit`
- Transcription backend: `faster-whisper`
- Supported media formats only:
  - `mp3`
  - `wav`
  - `m4a`
  - `mp4`
  - `mov`
- Primary goal: local transcription workflow with robust temporary file cleanup.

## 2) User Flow (Required Order)

1. User uploads a media file.
2. Only after upload is successful, parameter controls become visible.
3. User selects transcription quality.
4. User optionally enables partial transcription and sets start/end times.
5. User starts transcription.
6. App shows status/progress while running.
7. On success, app shows transcript text.
8. User can copy transcript to clipboard.
9. Temporary uploaded/derived files are deleted after success or abort (and also on failure).

## 3) Functional Requirements

### 3.1 Upload

- Use `st.file_uploader`.
- Restrict accepted file extensions to `mp3`, `wav`, `m4a`, `mp4`, `mov`.
- Save uploaded file into a temporary directory.
- Persist file metadata/path in `st.session_state`.
- Upload must happen before any parameter inputs are shown.

### 3.2 Quality Selection

- UI control with exactly two options:
  - `Low (faster)` -> model: `small`
  - `High (better quality)` -> model: `large-v3`
- Default selection: `Low (faster)`.

### 3.3 Partial Transcription Option

- Checkbox: `Transcribe partial range`.
- If unchecked: transcribe entire file.
- If checked: show `Start` and `End` time inputs.
- Time input format should be consistent (recommended: seconds as floats).
- Validation rules:
  - `start >= 0`
  - `end > start`
  - `end <= media_duration`
- Prevent transcription start when validation fails.

### 3.4 Media Segment Handling

- If partial mode is enabled:
  - Use `ffmpeg` to extract selected segment into a temp file.
  - Transcribe only the extracted segment.
- If partial mode is disabled:
  - Transcribe original uploaded file directly.

### 3.5 Transcription Execution

- Execute transcription using `faster-whisper` model selected by quality option.
- Show clear run status in UI:
  - `Preparing file...`
  - `Transcribing...`
  - `Done`
  - `Aborted`
  - `Failed`
- Disable `Transcribe` button while a job is running.

### 3.6 Abort Support

- Provide an `Abort` button visible/enabled only while transcribing.
- Aborting must:
  - cancel or terminate the running transcription task,
  - set status to aborted,
  - delete temp files,
  - show user message: `Transcription aborted.`

### 3.7 Transcript Display and Clipboard Copy

- On successful run, display transcript text in a large text area.
- Provide `Copy transcript` button that copies full transcript to system clipboard.
- Show user feedback after copy action (e.g., `Copied to clipboard`).

### 3.8 Temporary File Cleanup

- Cleanup must run in `finally`-equivalent logic.
- Files/directories to remove:
  - uploaded source file,
  - temporary partial segment file (if created),
  - temp directory (if empty).
- Cleanup must run after:
  - successful transcription,
  - aborted transcription,
  - failed transcription.

## 4) State Management Requirements

Use `st.session_state` to manage app state with keys similar to:

- `uploaded_file_path`
- `uploaded_filename`
- `transcribe_running` (bool)
- `abort_requested` (bool)
- `transcript_text`
- `status_message`
- `error_message`

State rules:

- Reset transcript when a new file is uploaded.
- Hide parameter controls until file upload is complete.
- Enable `Abort` only during active transcription.
- Prevent concurrent transcriptions.

## 5) Dependencies

- Python packages:
  - `streamlit`
  - `faster-whisper`
- System dependency:
  - `ffmpeg` available on PATH
- Optional clipboard helper package:
  - `streamlit-copy-to-clipboard`

## 6) Error Handling Requirements

- Unsupported file type: reject input with clear message.
- Missing `ffmpeg`: show explicit setup/runtime error.
- Invalid partial range: inline validation errors; block run.
- Runtime transcription exceptions: show failure message and still cleanup temp files.

## 7) Non-Functional Expectations

- Keep implementation modular (separate helpers for validation, media slicing, transcription, cleanup).
- Keep UI responsive and prevent duplicate submissions.
- Prefer deterministic behavior and explicit status messages over silent failures.

## 8) Acceptance Criteria

- App accepts only `mp3`, `wav`, `m4a`, `mp4`, `mov` uploads.
- Parameters cannot be configured before file upload.
- Low/high quality switch maps to two distinct model sizes.
- Full transcription works when partial option is disabled.
- Partial transcription correctly uses selected start/end range.
- Abort stops active job and displays aborted status.
- Transcript text is shown after success.
- Copy button copies transcript text to clipboard.
- Temporary files are removed on success, abort, and failure.
