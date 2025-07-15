from fastapi import FastAPI, Request, Response , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.router import router
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGIN")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/")
async def root():
    return {
        'status': 200,
        'message': 'success'
    }

app.include_router(router.router)
# app.include_router(webhook.router, prefix="/webhook")
