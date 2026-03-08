# Deadlift Local Review App

Local desktop-style app for reviewing deadlift videos and streaming AI coaching analysis from a local Ollama Qwen model.
Everything stays on localhost.

## Tech stack
- Frontend: TypeScript + React + Vite
- Backend: Python + FastAPI
- Model: Ollama (`qwen2.5:3b` by default)

## Project structure
```text
video_review_app/
├── README.md
├── context.md
├── skill.md
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   └── app/
│       ├── config.py
│       ├── main.py
│       ├── schemas.py
│       ├── routers/
│       │   ├── analysis.py
│       │   └── videos.py
│       └── services/
│           ├── inventory.py
│           ├── llm.py
│           └── summaries.py
└── frontend/
    ├── .env.example
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── api.ts
        ├── styles.css
        └── types.ts
```

## Folder wiring used by backend
Default configured folders:
- source inventory (`to_do`):
  - `/Users/jeremy/Desktop/exercise_tracker/deadlift/deadlift_videos/input/to_do`
- processed playable outputs (`_stitched`):
  - `/Users/jeremy/Desktop/exercise_tracker/deadlift/outputs/videos`
- summary CSV folder:
  - `/Users/jeremy/Desktop/exercise_tracker/deadlift/outputs/summaries`

Prompt context files:
- `skill.md`
- `context.md`

## Matching logic
### Video list
1. Scan source folder for `.mp4`, `.mov`, `.m4v`
2. Sort by source filename ascending
3. Match each source stem to processed file:
   - exact: `<source_stem>_stitched.<ext>`
   - fallback: `<source_stem>_<anything>_stitched.<ext>`
4. Show only matched items in UI (`Video 1`, `Video 2`, ...)

### Summary CSV for prompt
For selected source id (example `1706_short.mov`), backend uses source stem (`1706_short`) and loads all files in summaries folder matching:
- `<source_stem>_*_concentric_rep_metrics.csv`

Then it merges rows into one in-memory CSV and only includes selected high-level metrics.

## Prompt metric options exposed in UI
- Rep speed (m/s)
- Power
- Time to peak velocity
- Rounded back
- Rep duration

## API routes
- `GET /videos`
- `GET /video/{id}`
- `POST /stats-preview`
  - returns raw ground-truth stats text for selected video + selected metric filters
- `POST /analyze`
  - body:
    - `video_id`
    - `video_label`
    - `processed_filename`
    - `mode`
    - `selected_metrics` (list)
  - streams token chunks from Ollama in real time

## macOS requirements
- Python `3.11` recommended
- Node.js `20+`
- npm `10+`
- Ollama installed and running locally

## Setup option A: pip-only (venv)
```bash
cd /Users/jeremy/Desktop/exercise_tracker/deadlift/video_review_app/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Setup option B: conda
```bash
conda create -n deadlift-review python=3.11 -y
conda activate deadlift-review
cd /Users/jeremy/Desktop/exercise_tracker/deadlift/video_review_app/backend
pip install --upgrade pip
pip install -r requirements.txt
```

## Frontend install
```bash
cd /Users/jeremy/Desktop/exercise_tracker/deadlift/video_review_app/frontend
npm install
```

## Run Ollama
Make sure your model is available and running:
```bash
ollama list
ollama run qwen2.5:3b
```

## Run backend (Terminal 1)
```bash
cd /Users/jeremy/Desktop/exercise_tracker/deadlift/video_review_app/backend
source .venv/bin/activate  # skip if using conda env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run frontend (Terminal 2)
```bash
cd /Users/jeremy/Desktop/exercise_tracker/deadlift/video_review_app/frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:
- Frontend: `http://127.0.0.1:5173`
- FastAPI docs: `http://127.0.0.1:8000/docs`

## Optional env overrides
Use backend env vars (see `backend/.env.example`):
- `SOURCE_VIDEO_DIR`
- `PROCESSED_VIDEO_DIR`
- `SUMMARIES_DIR`
- `COACH_SKILL_PATH`
- `COACH_CONTEXT_PATH`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `OLLAMA_NUM_CTX`
- `OLLAMA_NUM_PREDICT`
- `PROMPT_SKILL_MAX_CHARS`
- `PROMPT_CONTEXT_MAX_CHARS`
- `PROMPT_CSV_MAX_ROWS`
- `RAW_STATS_MAX_ROWS`
- `VIDEO_TRANSCODE_CACHE_DIR`

## Notes
- No OpenCV windows.
- No cloud upload.
- All videos and metrics remain local.
- If a `_stitched` video codec is not browser-friendly (for example `mpeg4`), backend auto-transcodes to H.264 on first request and caches it in `backend/.cache/transcoded`. First load can take longer.
