from pathlib import Path
import os

# Defaults wired to your local workspace. Override with env vars if needed.
DEFAULT_SOURCE_DIR = "/Users/jeremy/Desktop/exercise_tracker/deadlift/deadlift_videos/input/to_do"
DEFAULT_PROCESSED_DIR = "/Users/jeremy/Desktop/exercise_tracker/deadlift/outputs/videos"
DEFAULT_SUMMARIES_DIR = "/Users/jeremy/Desktop/exercise_tracker/deadlift/outputs/summaries"

SOURCE_DIR = Path(os.getenv("SOURCE_VIDEO_DIR", DEFAULT_SOURCE_DIR)).expanduser().resolve()
PROCESSED_DIR = Path(os.getenv("PROCESSED_VIDEO_DIR", DEFAULT_PROCESSED_DIR)).expanduser().resolve()
SUMMARIES_DIR = Path(os.getenv("SUMMARIES_DIR", DEFAULT_SUMMARIES_DIR)).expanduser().resolve()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_MD_PATH = Path(os.getenv("COACH_SKILL_PATH", PROJECT_ROOT / "skill.md")).expanduser().resolve()
CONTEXT_MD_PATH = Path(os.getenv("COACH_CONTEXT_PATH", PROJECT_ROOT / "context.md")).expanduser().resolve()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_BASE_URL_FALLBACKS = [
    url.strip()
    for url in os.getenv("OLLAMA_BASE_URL_FALLBACKS", "http://localhost:11434").split(",")
    if url.strip()
]
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "4096"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "220"))

PROMPT_SKILL_MAX_CHARS = int(os.getenv("PROMPT_SKILL_MAX_CHARS", "2500"))
PROMPT_CONTEXT_MAX_CHARS = int(os.getenv("PROMPT_CONTEXT_MAX_CHARS", "3500"))
PROMPT_CSV_MAX_ROWS = int(os.getenv("PROMPT_CSV_MAX_ROWS", "80"))
RAW_STATS_MAX_ROWS = int(os.getenv("RAW_STATS_MAX_ROWS", "250"))

VIDEO_TRANSCODE_CACHE_DIR = Path(
    os.getenv("VIDEO_TRANSCODE_CACHE_DIR", PROJECT_ROOT / "backend" / ".cache" / "transcoded")
).expanduser().resolve()

ALLOWED_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
