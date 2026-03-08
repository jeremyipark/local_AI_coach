from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_CORS_ORIGINS
from app.routers.analysis import router as analysis_router
from app.routers.videos import router as videos_router

app = FastAPI(title="Deadlift Review App", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(videos_router)
app.include_router(analysis_router)
