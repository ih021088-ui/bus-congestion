from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.routers import current, predict, alert, stops

app = FastAPI(title="버스정류장 혼잡도 예측 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stops.router)
app.include_router(current.router)
app.include_router(predict.router)
app.include_router(alert.router)


@app.get("/health")
def health():
    return {"status": "ok"}
