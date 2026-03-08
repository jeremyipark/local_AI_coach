from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.config import RAW_STATS_MAX_ROWS, SUMMARIES_DIR
from app.schemas import AnalyzeRequest, StatsPreviewRequest, StatsPreviewResponse
from app.services.llm import stream_ollama_analysis
from app.services.summaries import build_raw_stats_text

router = APIRouter()


@router.post("/stats-preview", response_model=StatsPreviewResponse)
def stats_preview(payload: StatsPreviewRequest) -> StatsPreviewResponse:
    text, row_count, metric_labels = build_raw_stats_text(
        video_id=payload.video_id,
        video_label=payload.video_label,
        processed_filename=payload.processed_filename,
        selected_metrics=payload.selected_metrics,
        summaries_dir=SUMMARIES_DIR,
        max_rows=RAW_STATS_MAX_ROWS,
    )
    return StatsPreviewResponse(
        text=text,
        row_count=row_count,
        metric_labels=metric_labels,
    )


@router.post("/analyze")
async def analyze_video(payload: AnalyzeRequest) -> StreamingResponse:
    stream = stream_ollama_analysis(
        video_id=payload.video_id,
        video_label=payload.video_label,
        processed_filename=payload.processed_filename,
        mode=payload.mode,
        selected_metrics=payload.selected_metrics,
    )
    return StreamingResponse(stream, media_type="text/plain; charset=utf-8")
