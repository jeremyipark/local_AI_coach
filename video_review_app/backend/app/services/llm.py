import json
from pathlib import Path
from typing import AsyncIterator

import httpx

from app.config import (
    CONTEXT_MD_PATH,
    OLLAMA_BASE_URL,
    OLLAMA_BASE_URL_FALLBACKS,
    OLLAMA_MODEL,
    OLLAMA_NUM_CTX,
    OLLAMA_NUM_PREDICT,
    PROMPT_CONTEXT_MAX_CHARS,
    PROMPT_CSV_MAX_ROWS,
    PROMPT_SKILL_MAX_CHARS,
    SKILL_MD_PATH,
    SUMMARIES_DIR,
)
from app.services.summaries import METRIC_DEFINITIONS, load_merged_metrics_csv


def _read_text(path: Path, max_chars: int | None = None) -> str:
    if not path.exists() or not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    if max_chars is not None and len(text) > max_chars:
        return text[:max_chars].rstrip() + "\n\n[...truncated for prompt budget...]"
    return text


def _metric_keys_or_default(selected_metrics: list[str]) -> list[str]:
    if not selected_metrics:
        return list(METRIC_DEFINITIONS.keys())
    return [key for key in selected_metrics if key in METRIC_DEFINITIONS]


def _build_user_prompt(
    video_id: str,
    video_label: str | None,
    processed_filename: str | None,
    mode: str,
    selected_metrics: list[str],
) -> tuple[str, int, list[str]]:
    source_stem = Path(video_id).stem
    metrics_csv, rep_count, metric_labels = load_merged_metrics_csv(
        source_stem=source_stem,
        summaries_dir=SUMMARIES_DIR,
        selected_metrics=selected_metrics,
        processed_filename=processed_filename,
        max_rows=PROMPT_CSV_MAX_ROWS,
    )

    selected_metric_keys = _metric_keys_or_default(selected_metrics)

    if not metrics_csv:
        prompt = (
            f"Selected video label: {video_label or 'Video'}\n"
            f"Selected video id: {video_id}\n"
            f"Analysis mode: {mode}\n"
            "No matched concentric rep metrics CSV rows were found for this selection. "
            "Explain what is missing and what file naming to check."
        )
        return prompt, 0, metric_labels

    metric_list = ", ".join(metric_labels)
    metric_key_list = ", ".join(selected_metric_keys)

    prompt = f"""
Selected video label: {video_label or "Video"}
Selected video id: {video_id}
Analysis mode: {mode}
Selected metric keys: {metric_key_list}
Selected metrics: {metric_list}
Total reps loaded: {rep_count}

Task:
1. Interpret only the supplied metrics and selected analysis mode.
2. Treat each summary_file as a separate session/set; do not merge different files into one continuous set.
3. Start with a concise summary.
4. Call out consistency, fatigue signals, and coaching next steps.
5. Do not overclaim certainty.
6. Mention caveats when data is limited.
7. Return plain text only. Do not use markdown headings, bullet markers, or code fences.
8. Keep the output short: 4 to 7 sentences max.
9. Refer to the selection as "{video_label or "Video"}" and do not mention raw filenames.

Merged metrics CSV:
```csv
{metrics_csv}
```
""".strip()

    return prompt, rep_count, metric_labels


async def stream_ollama_analysis(
    video_id: str,
    video_label: str | None,
    processed_filename: str | None,
    mode: str,
    selected_metrics: list[str],
) -> AsyncIterator[str]:
    """Stream real tokens from local Ollama (Qwen)."""

    coach_skill = _read_text(SKILL_MD_PATH, max_chars=PROMPT_SKILL_MAX_CHARS)
    coaching_context = _read_text(CONTEXT_MD_PATH, max_chars=PROMPT_CONTEXT_MAX_CHARS)
    user_prompt, rep_count, metric_labels = _build_user_prompt(
        video_id=video_id,
        video_label=video_label,
        processed_filename=processed_filename,
        mode=mode,
        selected_metrics=selected_metrics,
    )

    system_prompt = (
        "You are a local deadlift coaching assistant. "
        "Use the provided coaching skill and context as operating constraints. "
        "Output plain text only (no markdown).\n\n"
        f"# Skill\n{coach_skill}\n\n"
        f"# Context\n{coaching_context}"
    )

    if rep_count == 0:
        yield "No matched summary rows found for this video. "
        yield "Expected files like '<source_stem>_*_concentric_rep_metrics.csv' in summaries."
        return

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {"num_ctx": OLLAMA_NUM_CTX, "num_predict": OLLAMA_NUM_PREDICT},
        "stream": True,
    }

    base_urls = [OLLAMA_BASE_URL] + [
        url for url in OLLAMA_BASE_URL_FALLBACKS if url != OLLAMA_BASE_URL
    ]

    last_error: str | None = None

    for base_url in base_urls:
        url = f"{base_url.rstrip('/')}/api/chat"
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        data = json.loads(line)
                        if "error" in data:
                            yield f"\n[Ollama error] {data['error']}"
                            return

                        message = data.get("message") or {}
                        content = message.get("content", "")
                        if content:
                            yield content

                        if data.get("done"):
                            return
        except httpx.HTTPError as exc:
            last_error = f"{url}: {exc}"
            continue

    tried = ", ".join(base_urls)
    yield (
        "\n[Connection error] Could not reach Ollama. "
        f"Tried: {tried}. Last error: {last_error}. "
        "Start Ollama with 'ollama serve' and verify with "
        "'curl http://127.0.0.1:11434/api/tags'."
    )
