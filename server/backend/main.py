from fastapi import FastAPI #type: ignore
from fastapi.middleware.cors import CORSMiddleware #type: ignore
from api.api import api_router

origins = ["..."]

app = FastAPI(title="RSA Monitoring")

app.include_router(api_router, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)