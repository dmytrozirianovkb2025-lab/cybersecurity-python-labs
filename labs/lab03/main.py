from contextlib import asynccontextmanager
from typing import Any, Dict
from fastapi import FastAPI

from shared import student
from labs.lab03.config import DOMAIN_NAME, THRESHOLD, UNIT, VARIANT_NUMBER
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title=f"Lab 03 API - Варіант {VARIANT_NUMBER}",
    description=(
        f"Предметна область: {DOMAIN_NAME}. "
        f"Одиниця вимірювання: {UNIT}. Поріг: {THRESHOLD}."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(records.router)


@app.get("/ping", tags=["Service"])
def ping() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/student", tags=["Service"])
def get_student() -> Dict[str, Any]:
    return {
        "student_name": getattr(student, "STUDENT_NAME", "Студент"),
        "group_name": getattr(student, "GROUP_NAME", "Група"),
        "variant_number": getattr(student, "VARIANT", VARIANT_NUMBER),
    }
