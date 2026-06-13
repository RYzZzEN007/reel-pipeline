import argparse
import os
import sys
import time

from ingest import validate_file, get_metadata
from face_blur import process_video
from captions import add_captions


def run_pipeline(input_path, hook, watermark, style, keep_temp):
    start = time.time()

    # ---- Stage 1: ingest ----
    print("\n[1/3] Ingesting...")
    validate_file(input_path)
    meta = get_metadata(input_path)
    print(f"      {meta['width']}x{meta['height']}, "
          f"{meta['duration_sec']:.1f}s, {meta['fps']}fps")
    if meta["height"] <= meta["width"]:
        print("      ⚠️  not vertical — reel will be letterboxed")

    name, _ = os.path.splitext(os.path.basename(input_path))
    os.makedirs("output", exist_ok=True)
    temp_anon = f"output/{name}_anon.mp4"
    final_out = f"output/{name}_reel.mp4"

    # ---- Stage 2: anonymize ----
    print(f"[2/3] Anonymizing faces ({style})...")
    process_video(input_path, temp_anon, style=style)

    # ---- Stage 3: captions + audio + encode ----
    print("[3/3] Burning captions, restoring audio, encoding...")
    add_captions(temp_anon, input_path, hook, watermark, final_out)

    if not keep_temp:
        os.remove(temp_anon)

    elapsed = time.time() - start
    print(f"\n✅ Reel ready: {final_out}")
    print(f"   Pipeline ran in {elapsed:.1f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Turn raw gym footage into a post-ready faceless reel."
    )
    parser.add_argument("input", help="path to the raw video file")
    parser.add_argument("--hook", default="", help="caption text (top-center)")
    parser.add_argument("--watermark", default="", help="brand handle (bottom)")
    parser.add_argument("--style", choices=["blur", "pixelate"],
                        default="blur", help="anonymization style")
    parser.add_argument("--keep-temp", action="store_true",
                        help="keep the intermediate anonymized file")
    args = parser.parse_args()

    run_pipeline(args.input, args.hook, args.watermark,
                 args.style, args.keep_temp)