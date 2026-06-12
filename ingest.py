import subprocess
import json
import os
import sys


def validate_file(path):
    """Check the input file exists and is a video we can work with."""
    if not os.path.exists(path):
        sys.exit(f"Error: file not found -> {path}")

    valid_extensions = (".mp4", ".mov", ".m4v")
    if not path.lower().endswith(valid_extensions):
        sys.exit(f"Error: unsupported format. Use: {valid_extensions}")


def get_metadata(path):
    """Ask ffprobe (ffmpeg's analyzer) for the video's vital stats."""
    cmd = [
        "ffprobe",
        "-v", "quiet",              # silence ffprobe's own chatter
        "-print_format", "json",    # give us machine-readable output
        "-show_streams",            # details of video/audio streams
        "-show_format",             # container info (duration, size)
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    # find the video stream (files also contain audio streams)
    video = next(s for s in data["streams"] if s["codec_type"] == "video")

    return {
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": round(eval(video["r_frame_rate"])),  # comes as "30000/1001"
        "duration_sec": float(data["format"]["duration"]),
        "size_mb": round(int(data["format"]["size"]) / 1_000_000, 1),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python ingest.py <video_file>")

    clip = sys.argv[1]
    validate_file(clip)
    meta = get_metadata(clip)

    print(f"\n📹 {os.path.basename(clip)}")
    for key, value in meta.items():
        print(f"   {key}: {value}")

    if meta["height"] <= meta["width"]:
        print("   ⚠️  horizontal clip — will need crop in later stage")
    else:
        print("   ✅ vertical — reel-ready orientation")