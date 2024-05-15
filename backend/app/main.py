from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.api.v1.routes import routers
from app.core.config import settings

app = FastAPI()
add_pagination(app)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.cors.origins,
    allow_methods=settings.cors.methods,
    allow_headers=settings.cors.headers,
)

app.include_router(routers, prefix="/api/v1")
