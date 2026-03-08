import csv
import io
from pathlib import Path


METRIC_DEFINITIONS: dict[str, dict[str, list[str] | str]] = {
    "rep_speed": {
        "label": "Rep speed (m/s)",
        "columns": ["mean_velocity_mps", "peak_velocity_mps"],
    },
    "power": {
        "label": "Power (W)",
        "columns": ["mean_power_w", "peak_power_w", "mean_positive_power_w"],
    },
    "time_to_peak_velocity": {
        "label": "Time to peak velocity (ms)",
        "columns": ["ttpv_ms"],
    },
    "back_rounding": {
        "label": "Rounded back", "columns": ["is_rounded"],
    },
    "rep_duration": {
        "label": "Rep duration (s)",
        "columns": ["duration_sec"],
    },
}


def _metric_columns(selected_metrics: list[str]) -> list[str]:
    selected = selected_metrics or list(METRIC_DEFINITIONS.keys())
    columns: list[str] = []

    for metric_key in selected:
        entry = METRIC_DEFINITIONS.get(metric_key)
        if not entry:
            continue

        metric_cols = entry["columns"]
        assert isinstance(metric_cols, list)
        for column in metric_cols:
            if column not in columns:
                columns.append(column)

    return columns


def _processed_summary_stem(processed_filename: str | None) -> str | None:
    if not processed_filename:
        return None

    stem = Path(processed_filename).stem
    if stem.endswith("_stitched"):
        return stem[: -len("_stitched")]
    return None


def _summary_metric_files(
    source_stem: str,
    summaries_dir: Path,
    processed_filename: str | None = None,
) -> list[Path]:
    if not summaries_dir.exists():
        return []

    processed_summary_stem = _processed_summary_stem(processed_filename)
    if processed_summary_stem:
        exact_path = summaries_dir / f"{processed_summary_stem}_concentric_rep_metrics.csv"
        if exact_path.exists() and exact_path.is_file():
            return [exact_path]
        # Do not fall back to other sessions when a specific processed render was selected.
        return []

    files = [
        path
        for path in summaries_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".csv"
        and path.name.endswith("_concentric_rep_metrics.csv")
        and (
            path.stem == f"{source_stem}_concentric_rep_metrics"
            or path.stem.startswith(f"{source_stem}_")
        )
    ]

    return sorted(files, key=lambda p: p.name)


def load_merged_metrics_csv(
    source_stem: str,
    summaries_dir: Path,
    selected_metrics: list[str],
    processed_filename: str | None = None,
    max_rows: int | None = None,
) -> tuple[str, int, list[str]]:
    """Build one merged CSV string across all matched summary files for a source stem."""

    metric_columns = _metric_columns(selected_metrics)
    metric_labels = [
        str(METRIC_DEFINITIONS[key]["label"])
        for key in (selected_metrics or list(METRIC_DEFINITIONS.keys()))
        if key in METRIC_DEFINITIONS
    ]

    files = _summary_metric_files(
        source_stem=source_stem,
        summaries_dir=summaries_dir,
        processed_filename=processed_filename,
    )
    if not files:
        return "", 0, metric_labels

    base_columns = ["summary_file", "set_index", "rep_number", "rep_label"]

    rows: list[dict[str, str]] = []
    for file_path in files:
        with file_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                merged_row: dict[str, str] = {
                    "summary_file": file_path.name,
                    "set_index": row.get("set_index", ""),
                    "rep_number": row.get("rep_number", ""),
                    "rep_label": row.get("rep_label", ""),
                }
                for column in metric_columns:
                    merged_row[column] = row.get(column, "")
                rows.append(merged_row)
                if max_rows is not None and len(rows) >= max_rows:
                    break
            if max_rows is not None and len(rows) >= max_rows:
                break

    output_columns = base_columns + metric_columns
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=output_columns)
    writer.writeheader()
    writer.writerows(rows)

    return buffer.getvalue(), len(rows), metric_labels


def build_raw_stats_text(
    video_id: str,
    video_label: str | None,
    processed_filename: str | None,
    selected_metrics: list[str],
    summaries_dir: Path,
    max_rows: int,
) -> tuple[str, int, list[str]]:
    source_stem = Path(video_id).stem
    csv_text, row_count, metric_labels = load_merged_metrics_csv(
        source_stem=source_stem,
        summaries_dir=summaries_dir,
        selected_metrics=selected_metrics,
        processed_filename=processed_filename,
        max_rows=max_rows,
    )

    if not csv_text:
        return (
            "No matched summary rows found for this video selection.",
            0,
            metric_labels,
        )

    rows = list(csv.DictReader(io.StringIO(csv_text)))
    selected = selected_metrics or list(METRIC_DEFINITIONS.keys())

    def numeric_values(column: str) -> list[float]:
        values: list[float] = []
        for row in rows:
            value = row.get(column, "")
            if value in ("", None):
                continue
            try:
                values.append(float(value))
            except ValueError:
                continue
        return values

    def mean_or_none(column: str) -> float | None:
        values = numeric_values(column)
        if not values:
            return None
        return sum(values) / len(values)

    lines: list[str] = [f"Reps analyzed: {row_count}"]

    for metric_key in selected:
        if metric_key == "time_to_peak_velocity":
            avg = mean_or_none("ttpv_ms")
            if avg is not None:
                lines.append(f"Avg TTPV: {avg:.1f} ms")
        elif metric_key == "rep_duration":
            avg = mean_or_none("duration_sec")
            if avg is not None:
                lines.append(f"Avg rep duration: {avg:.3f} s")
        elif metric_key == "rep_speed":
            avg_mean = mean_or_none("mean_velocity_mps")
            avg_peak = mean_or_none("peak_velocity_mps")
            speed_parts: list[str] = []
            if avg_mean is not None:
                speed_parts.append(f"- Avg mean: {avg_mean:.3f} m/s")
            if avg_peak is not None:
                speed_parts.append(f"- Avg peak: {avg_peak:.3f} m/s")
            if speed_parts:
                lines.append("Rep speed:")
                lines.extend(speed_parts)
        elif metric_key == "power":
            avg_mean = mean_or_none("mean_power_w")
            avg_peak = mean_or_none("peak_power_w")
            avg_pos = mean_or_none("mean_positive_power_w")
            power_parts: list[str] = []
            if avg_mean is not None:
                power_parts.append(f"- Avg mean: {avg_mean:.1f} W")
            if avg_peak is not None:
                power_parts.append(f"- Avg peak: {avg_peak:.1f} W")
            if avg_pos is not None:
                power_parts.append(f"- Avg positive: {avg_pos:.1f} W")
            if power_parts:
                lines.append("Power:")
                lines.extend(power_parts)
        elif metric_key == "back_rounding":
            rounded_values = [
                str(row.get("is_rounded", "")).strip().lower()
                for row in rows
                if str(row.get("is_rounded", "")).strip() != ""
            ]
            if rounded_values:
                rounded_count = sum(1 for value in rounded_values if value in {"true", "1", "yes"})
                pct = (rounded_count / len(rounded_values)) * 100
                lines.append(
                    f"Rounded back reps: {rounded_count}/{len(rounded_values)} ({pct:.1f}%)"
                )

    text = "\n".join(lines)
    return text, row_count, metric_labels
