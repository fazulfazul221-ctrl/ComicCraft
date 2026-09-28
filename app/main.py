import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Web application using Google Gemini and Stable Diffusion to generate personalized comic book stories and illustrations.",
    version="1.0.0"
)

# Ensure required directories exist
os.makedirs("static/panels", exist_ok=True)
os.makedirs("static/exports", exist_ok=True)
os.makedirs("static/fonts", exist_ok=True)
os.makedirs("static/images", exist_ok=True)

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include application routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
