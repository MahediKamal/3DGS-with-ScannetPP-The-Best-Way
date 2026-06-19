#!/usr/bin/env python3
"""
Extract only the RGB frames that are registered in the COLMAP reconstruction
(iphone/colmap/images.txt) for a ScanNet++ iPhone scene, and save them to an
images folder.

Frame selection is driven ENTIRELY by images.txt — FRAME_STRIDE and
pose_intrinsic_imu.json are not used for selection. This guarantees a 1:1
match between the extracted images and the frames COLMAP actually registered
during SfM (which is typically a subset of the full raw rgb.mkv capture).

Each frame is saved using its exact COLMAP name, e.g.:
    <OUTPUT_DIR>/frame_000000.png

Usage:
    python extract_colmap_frames.py \
        --iphone-dir datasets/scannetpp/data/39f36da05b/iphone \
        --output-dir images
"""

import argparse
import re
import sys
from pathlib import Path

import cv2


def parse_colmap_images_txt(images_txt_path: Path) -> dict[int, str]:
    """
    Parse COLMAP images.txt and return {frame_idx: image_name} for every
    registered image.

    images.txt format (COLMAP text model), one image per pair of lines:
        Line 1: IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME
        Line 2: POINTS2D[] (skipped)
    Header/comment lines start with '#' and are ignored.
    """
    if not images_txt_path.exists():
        sys.exit(f"ERROR: COLMAP images.txt not found at {images_txt_path}")

    with images_txt_path.open() as fh:
        # Only drop comment lines here — do NOT drop blank lines, since a
        # frame with zero POINTS2D produces a blank second line, and removing
        # it would shift the data/POINTS2D pairing for every entry after it.
        lines = [l for l in fh if not l.startswith("#")]

    name_by_frame_idx: dict[int, str] = {}

    # Image entries occupy every other line (data line, then POINTS2D line).
    for i in range(0, len(lines), 2):
        parts = lines[i].split()
        if len(parts) < 10:
            continue
        image_name = parts[9]  # NAME field, e.g. "frame_000000.jpg"
        stem = Path(image_name).stem
        m = re.search(r"(\d+)$", stem)
        if not m:
            print(f"  Warning: could not parse a frame index from '{image_name}' — skipped")
            continue
        frame_idx = int(m.group(1))
        name_by_frame_idx[frame_idx] = image_name

    if not name_by_frame_idx:
        sys.exit(f"ERROR: no registered images found in {images_txt_path}")

    return name_by_frame_idx


def extract_colmap_frames(iphone_dir: Path, output_dir: Path) -> None:
    rgb_mkv_path = iphone_dir / "rgb.mkv"
    colmap_images_txt = iphone_dir / "colmap" / "images.txt"

    if not rgb_mkv_path.exists():
        sys.exit(f"ERROR: rgb.mkv not found at {rgb_mkv_path}")

    # ── Frames registered by COLMAP — this is the ONLY selection source ─────
    name_by_frame_idx = parse_colmap_images_txt(colmap_images_txt)
    frame_indices = sorted(name_by_frame_idx.keys())
    print(f"COLMAP images.txt : {len(frame_indices)} registered frames")

    # ── Open video and extract ───────────────────────────────────────────────
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(rgb_mkv_path))
    if not cap.isOpened():
        sys.exit(f"ERROR: could not open {rgb_mkv_path}")

    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"rgb.mkv           : {total_video_frames} frames")

    n_saved = 0
    n_failed = 0

    for frame_idx in frame_indices:
        if frame_idx >= total_video_frames:
            print(f"  Warning: COLMAP frame {frame_idx} out of range of rgb.mkv ({total_video_frames}) — skipped")
            n_failed += 1
            continue

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, bgr = cap.read()
        if not ok:
            print(f"  Warning: could not read frame {frame_idx} — skipped")
            n_failed += 1
            continue

        # Save under the exact stem COLMAP uses, as a .jpg regardless of the
        # original extension recorded in images.txt.
        stem = Path(name_by_frame_idx[frame_idx]).stem
        out_path = output_dir / f"{stem}.jpg"
        cv2.imwrite(str(out_path), bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
        n_saved += 1

    cap.release()

    print(f"\nSaved  : {n_saved} images")
    print(f"Failed : {n_failed}")
    print(f"Output : {output_dir.resolve()}")

    if n_saved != len(frame_indices):
        print(
            f"\nNote: {len(frame_indices)} frames are registered in COLMAP but only "
            f"{n_saved} were extracted — see warnings above (likely rgb.mkv frame-count "
            f"mismatch or read failures)."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract only the frames registered in COLMAP's images.txt "
                    "for a ScanNet++ iPhone scene, and save them to an images folder."
    )
    parser.add_argument(
        "--iphone-dir",
        type=Path,
        required=True,
        help="Path to the scene's iphone/ directory "
             "(contains rgb.mkv and colmap/images.txt).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("images"),
        help="Folder to save extracted frames into (default: ./images).",
    )
    args = parser.parse_args()

    extract_colmap_frames(
        iphone_dir=args.iphone_dir,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()