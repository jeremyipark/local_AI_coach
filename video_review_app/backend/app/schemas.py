from pydantic import BaseModel, Field


class VideoItem(BaseModel):
    id: str
    label: str
    source_filename: str
    processed_filename: str


class StatsPreviewRequest(BaseModel):
    video_id: str
    video_label: str | None = None
    processed_filename: str | None = None
    selected_metrics: list[str] = Field(default_factory=list)


class StatsPreviewResponse(BaseModel):
    text: str
    row_count: int
    metric_labels: list[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    video_id: str
    video_label: str | None = None
    processed_filename: str | None = None
    mode: str = "Technique"
    selected_metrics: list[str] = Field(default_factory=list)
