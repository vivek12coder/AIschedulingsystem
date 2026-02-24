from fastapi import FastAPI
from pydantic import BaseModel

from scheduler.models import Schedule, ScheduleInput
from scheduler.solver import generate_schedule
from scheduler.conflict_resolver import detect_conflicts, resolve_and_score

app = FastAPI(
    title="AI Timetable Scheduler",
    description="AI-powered timetable scheduling system using CSP and Genetic Algorithm",
    version="1.0.0",
)


class ValidateRequest(BaseModel):
    schedule: Schedule
    schedule_input: ScheduleInput


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/schedule/generate", response_model=Schedule)
def schedule_generate(
    schedule_input: ScheduleInput,
    optimize: bool = True,
    generations: int = 50,
    population_size: int = 30,
):
    return generate_schedule(
        schedule_input,
        optimize=optimize,
        generations=generations,
        population_size=population_size,
    )


@app.post("/schedule/validate")
def schedule_validate(request: ValidateRequest):
    return detect_conflicts(request.schedule.entries, request.schedule_input)


@app.post("/schedule/resolve", response_model=Schedule)
def schedule_resolve(request: ValidateRequest):
    return resolve_and_score(request.schedule.entries, request.schedule_input)
