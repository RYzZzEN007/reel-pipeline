## How It Works

**ingest.py** — Validates the input and extracts metadata (resolution, fps,
duration) via ffprobe. Handles a real-world iPhone quirk: footage is stored
sideways with a rotation flag rather than physically rotated, so raw
dimensions report vertical clips as landscape. The module reads the rotation
flag from `side_data_list` and corrects width/height accordingly.

**face_blur.py** — Detects and anonymizes all faces frame-by-frame (also
anonymizes bystanders). Built in three iterations on real footage:
1. *Haar cascade* — fast but failed on tilted-head poses and false-triggered
   on gym equipment and skin regions.
2. *YuNet (DNN, ONNX)* — migrated to OpenCV's deep-learning detector; fixed
   angle misses, real faces detect at 0.86–0.95 confidence.
3. *False-positive filtering* — added a `--debug` mode that renders detection
   boxes + confidence scores. Used it to identify torso false positives
   (0.60–0.81 confidence, tall-rectangle shaped) and eliminated them with a
   confidence threshold (0.65) plus a geometric aspect-ratio filter, rather
   than fragile threshold-only tuning.

Anonymization uses a face-size-adaptive blur (or pixelate) composited through
a feathered elliptical mask, so strength scales with subject distance and
blends naturally instead of showing a hard rectangle. Temporal persistence
keeps the last-known face region anonymized for 10 frames after detection
drops, bridging momentary misses.

**captions.py** — Single ffmpeg pass that burns the hook caption (top-center,
outlined) and a translucent watermark, while mapping video from the
anonymized file and audio from the untouched original (`-map 0:v -map 1:a?`),
restoring sound that OpenCV's video-only writer drops. Encodes to Instagram
spec: H.264, CRF 20, AAC, yuv420p.

**pipeline.py** — Orchestrates all three stages behind one argparse CLI by
importing each module's functions, timing the full run, and writing output to
a clean `output/` folder.

## Tech Stack
Python 3 · OpenCV (YuNet DNN face detection) · ffmpeg / ffmpeg-python ·
NumPy

## Results
| | Manual (VN) | Pipeline |
|---|---|---|
| Time per reel | ~[X] min | ~41 sec |

*(Measured on an 18s, 1080×1920 clip.)*