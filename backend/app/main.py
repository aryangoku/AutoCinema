from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AutoCinema", version="0.2.0")


class Health(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = "0.2.0"
    milestone: int = 1


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health()
