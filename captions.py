import subprocess
import sys
import os

FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"  # ships with macOS


def escape_text(text):
    """ffmpeg's drawtext treats some characters specially — escape them."""
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def add_captions(video_path, audio_source, hook, watermark, output_path):
    """Burn hook text + watermark onto video, re-attach original audio."""

    filters = []

    if hook:
        filters.append(
            f"drawtext=fontfile='{FONT}':text='{escape_text(hook)}':"
            "fontsize=64:fontcolor=white:borderw=4:bordercolor=black:"
            "x=(w-text_w)/2:y=h*0.12"
        )

    if watermark:
        filters.append(
            f"drawtext=fontfile='{FONT}':text='{escape_text(watermark)}':"
            "fontsize=36:fontcolor=white@0.6:"
            "x=(w-text_w)/2:y=h*0.92"
        )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,              # input 0: anonymized video (no audio)
        "-i", audio_source,            # input 1: ORIGINAL clip (has audio)
        "-map", "0:v",                 # video from input 0
        "-map", "1:a?",                # audio from input 1, if present
        "-vf", ",".join(filters) if filters else "null",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-1500:])
        sys.exit("Error: ffmpeg failed (see log above)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit('Usage: python captions.py <anonymized_video> <original_video> '
                 '"hook text" ["watermark"]')

    blurred = sys.argv[1]
    original = sys.argv[2]
    hook = sys.argv[3] if len(sys.argv) > 3 else ""
    watermark = sys.argv[4] if len(sys.argv) > 4 else ""

    name, _ = os.path.splitext(os.path.basename(blurred))
    output = f"{name}_final.mp4"

    add_captions(blurred, original, hook, watermark, output)
    print(f"✅ saved -> {output}")