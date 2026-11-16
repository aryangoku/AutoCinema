from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AutoCinema", version="0.1.0")


class Health(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = "0.1.0"
    milestone: int = 0


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health()
