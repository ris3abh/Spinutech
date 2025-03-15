from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import auth, users, clients, content, preferences, seo

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["authentication"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(clients.router, prefix=settings.API_V1_STR, tags=["clients"])
app.include_router(content.router, prefix=settings.API_V1_STR, tags=["content"])
app.include_router(preferences.router, prefix=settings.API_V1_STR, tags=["preferences"])
app.include_router(seo.router, prefix=settings.API_V1_STR, tags=["seo"])


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "SEO Content API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)