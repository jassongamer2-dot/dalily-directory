from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import companies, ingestion, review_queue, industries

app = FastAPI(title="Industrial Directory API")

# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # <-- No slash at the end!
        "https://dalily-directory-l62hrw58d-jassongamer2-9403s-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router)
app.include_router(ingestion.router)
app.include_router(review_queue.router)
app.include_router(industries.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
