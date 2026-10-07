from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import wardrobe as wardrobe_router
from app.routers import weather as weather_router


# Create table if not exists
@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


# Create FastAPI app
app = FastAPI(title="Digital Wardrobe Mirror API", version="1.0.0", lifespan=lifespan)

# Mount routers
app.include_router(wardrobe_router.router, prefix="/api/wardrobe", tags=["wardrobe"])
app.include_router(weather_router.router, prefix="/api/weather", tags=["weather"])


@app.get("/")
async def root():
    return {"message": "Digital Wardrobe Mirror API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
