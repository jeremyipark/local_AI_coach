from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Iterable


SOURCE_EXTS = {".mp4", ".mov", ".m4v"}
PROCESSED_EXTS = {".mp4", ".mov", ".m4v"}


@dataclass
class InventoryItem:
    id: str
    label: str
    source_path: Path
    processed_path: Path


def _is_supported(path: Path, exts: set[str]) -> bool:
    return path.is_file() and path.suffix.lower() in exts


def _is_readable_video(path: Path) -> bool:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name",
        "-of",
        "default=nw=1:nk=1",
        str(path),
    ]
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and bool(result.stdout.strip())


def _pick_latest_readable(candidates: list[Path]) -> Path | None:
    for candidate in sorted(candidates, key=lambda p: p.name, reverse=True):
        if _is_readable_video(candidate):
            return candidate
    return None


def _find_match(source_stem: str, processed_candidates: Iterable[Path]) -> Path | None:
    exact_stem = f"{source_stem}_stitched"

    exact = [p for p in processed_candidates if p.stem == exact_stem]
    exact_match = _pick_latest_readable(exact)
    if exact_match:
        return exact_match

    # Preferred fallback: <source_stem>_<YYYYMMDD-HHMMSS>_stitched.ext
    ts_pattern = re.compile(rf"^{re.escape(source_stem)}_\d{{8}}-\d{{6}}_stitched$")
    timestamped = [p for p in processed_candidates if ts_pattern.match(p.stem)]
    timestamped_match = _pick_latest_readable(timestamped)
    if timestamped_match:
        return timestamped_match

    # Broad fallback for legacy variants like: <source_stem>_<anything>_stitched.ext
    prefix = [
        p
        for p in processed_candidates
        if p.stem.startswith(f"{source_stem}_") and p.stem.endswith("_stitched")
    ]
    prefix_match = _pick_latest_readable(prefix)
    if prefix_match:
        return prefix_match

    return None


def build_inventory(source_dir: Path, processed_dir: Path) -> list[InventoryItem]:
    if not source_dir.exists() or not processed_dir.exists():
        return []

    source_files = [p for p in source_dir.iterdir() if _is_supported(p, SOURCE_EXTS)]
    source_files.sort(key=lambda p: p.name)

    # Recursive scan allows stitched outputs saved under nested folders (e.g. successes/).
    processed_files = [
        p
        for p in processed_dir.rglob("*")
        if _is_supported(p, PROCESSED_EXTS) and p.stem.endswith("_stitched")
    ]

    inventory: list[InventoryItem] = []

    for source_path in source_files:
        match = _find_match(source_path.stem, processed_files)
        if not match:
            continue

        label = f"Video {len(inventory) + 1}"
        inventory.append(
            InventoryItem(
                id=source_path.name,
                label=label,
                source_path=source_path,
                processed_path=match,
            )
        )

    return inventory
