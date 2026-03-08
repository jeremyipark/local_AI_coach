import mimetypes

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import PROCESSED_DIR, SOURCE_DIR, VIDEO_TRANSCODE_CACHE_DIR
from app.schemas import VideoItem
from app.services.inventory import build_inventory
from app.services.video_playback import get_browser_playable_video_path

router = APIRouter()


@router.get("/videos", response_model=list[VideoItem])
def get_videos() -> list[VideoItem]:
    inventory = build_inventory(SOURCE_DIR, PROCESSED_DIR)
    return [
        VideoItem(
            id=item.id,
            label=item.label,
            source_filename=item.source_path.name,
            processed_filename=item.processed_path.name,
        )
        for item in inventory
    ]


@router.get("/video/{video_id}")
def get_video(video_id: str) -> FileResponse:
    inventory = build_inventory(SOURCE_DIR, PROCESSED_DIR)
    lookup = {item.id: item for item in inventory}
    item = lookup.get(video_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Video not found")

    try:
        playable_path = get_browser_playable_video_path(
            video_path=item.processed_path,
            cache_dir=VIDEO_TRANSCODE_CACHE_DIR,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Video is not streamable: {exc}",
        ) from exc
    media_type, _ = mimetypes.guess_type(playable_path.name)

    return FileResponse(
        path=playable_path,
        media_type=media_type or "application/octet-stream",
        filename=playable_path.name,
    )
