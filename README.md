# Reel Pipeline 🎬

A Python video-processing pipeline that automates editing for faceless
fitness content — face anonymization, caption burning, and Instagram-ready
export — turning raw gym footage into post-ready reels with one command.

## Why
Editing each reel manually (blurring faces, adding text, re-exporting)
took significant time per video. This tool automates the repetitive
technical steps so creative effort goes into content, not editing.

## Pipeline
raw clip → ingest (validate/metadata) → face blur (OpenCV) →
caption burn (ffmpeg) → export (1080x1920, H.264)

## Tech Stack
- Python 3
- OpenCV — face detection & blurring
- ffmpeg / ffmpeg-python — video processing, text overlay, encoding

## Usage
```bash
python pipeline.py input.mp4 --hook "your caption here"
```

## Modules

### 1. ingest.py ✅
Validates input files and extracts metadata (resolution, fps, duration,
file size) using ffprobe with JSON output parsed via subprocess.

**Real-world fix:** iPhone footage stores the video stream sideways with
a rotation flag (e.g. `rotation: -90`) instead of physically rotating
pixels. Raw ffprobe dimensions reported my vertical clips as 1920x1080
landscape. The module now reads `side_data_list` for the rotation flag
and swaps width/height when rotation is ±90°.

### 2. face_blur.py 🚧 in progress