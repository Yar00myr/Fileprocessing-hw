from fastapi import FastAPI

app = FastAPI()

from .routes import file_router

app.include_router(file_router)