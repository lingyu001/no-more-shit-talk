from dotenv import load_dotenv
from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles  # comment out if not using
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Stock Market Analysis API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the test UI
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routes
app.include_router(api_router, prefix="/api/v1") 