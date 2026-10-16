from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import outfits as outfits_router
from app.routers import wardrobe as wardrobe_router
from app.routers import weather as weather_router


# Create table if not exists
@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


# Create FastAPI app
app = FastAPI(title="Digital Wardrobe Mirror API", version="1.0.0", lifespan=lifespan)

# Allow the Vite dev server to call the API directly if the proxy is not used.
# Same-origin /api calls via the Vite proxy do not need CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(wardrobe_router.router, prefix="/api/wardrobe", tags=["wardrobe"])
app.include_router(weather_router.router, prefix="/api/weather", tags=["weather"])
app.include_router(outfits_router.router, prefix="/api/outfits", tags=["outfits"])


@app.get("/")
async def root():
    return {"message": "Digital Wardrobe Mirror API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
